# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer.c

## Purpose

`fw_tracer.c` implements mlx5 firmware trace collection. It allocates a DMA log buffer, creates an mkey for firmware writes, reads firmware string databases, acquires tracer ownership, handles firmware tracer EQ events, decodes string/timestamp trace records, emits the `mlx5_fw` tracepoint, and stores recent decoded traces for devlink health dumps.

## Important APIs, Types, and Functions

- `mlx5_fw_tracer_create()` allocates software state, workqueue, log buffer, string DB buffers, and saved-trace storage after querying `MTRC_CAP`.
- `mlx5_fw_tracer_init()` allocates PD/mkey, registers an EQ notifier, queues string DB reading, and starts the tracer.
- `mlx5_fw_tracer_cleanup()` unregisters notifier, cancels work, releases ownership, and destroys PD/mkey.
- `mlx5_fw_tracer_destroy()` frees software resources, string DB buffers, log buffer, saved trace mutex, workqueue, and tracer object.
- `mlx5_fw_tracer_reload()` stops tracing, recreates string DB state, and reinitializes.
- `fw_tracer_event()` dispatches ownership change, traces available, and strings DB update EQ subtypes to work items.
- `mlx5_fw_tracer_handle_traces()` consumes the circular trace buffer, detects overwritten blocks, parses records, and rearms firmware events.
- `mlx5_tracer_handle_string_trace()` and timestamp handling assemble multi-record formatted messages.
- `mlx5_fw_tracer_get_saved_traces_objects()` emits saved traces into a devlink fmsg.
- `mlx5_fw_tracer_trigger_core_dump_general()` writes the core dump register and drains traces synchronously.

## Control Flow

Creation probes tracer registers and `trace_to_memory`, then records string DB addresses/sizes and current owner state. Initialization reads string DB asynchronously if not loaded, marks tracer UP under `state_lock`, allocates hardware resources, registers the EQ notifier, and calls `mlx5_fw_tracer_start()`. Start tries to acquire ownership; ownership failure is nonfatal because later events may grant it. When owned, it writes `MTRC_CONF` with trace mode, buffer size, and mkey, then enables/arms tracing with `MTRC_CTRL`.

On traces-available EQ events, the handler copies one 256-byte block from the DMA buffer, parses the final timestamp, and advances while block timestamps are newer than `last_timestamp`. It compares the previous block timestamp to detect wrap overwrite and logs lost events. String events either start a format string, append parameters, or fall back to raw output. Timestamp events flush ready strings with reconstructed full timestamps.

## State and Persistence Behavior

Persistent tracer state includes firmware ownership, tracer version, string DB metadata and buffers, DMA log buffer, PD/mkey, circular consumer index, `last_timestamp`, hash table of in-progress formatted messages, ready list, saved trace ring (`SAVED_TRACES_NUM`), workqueue items, EQ notifier, and state bits (`UP`, `RECREATE_DB`). Saved traces are a ring protected by `st_arr.lock`.

Firmware-visible state is changed through `MTRC_CAP`, `MTRC_CONF`, `MTRC_CTRL`, `MTRC_STDB`, and `CORE_DUMP` registers.

## Dependencies and Integration Points

Depends on mlx5 register access, EQ notifier infrastructure, DMA mapping, PD/mkey allocation, Linux workqueues, jhash, tracepoint `mlx5_fw`, and devlink fmsg. It is integrated with health reporters and firmware diagnostic workflows.

## Risks and Edge Cases

- `mlx5_tracer_get_string()` uses strict `str_ptr > base && str_ptr < base + size`; a string exactly at the base address would not match.
- Format strings are modified in place to replace `%llx` with `%x%x`; string DB buffers must be writable and not shared as immutable data.
- The saved traces dump loop stops before `end_index`, so it may omit the newest entry depending on ring index semantics.
- Work cancellation intentionally uses `cancel_work()` rather than `cancel_work_sync()` for `update_db_work` during cleanup because cleanup can run from that work item; this requires careful sequencing in future changes.
- Heavy trace rates can overwrite circular blocks before software handles them, detected only by timestamp comparison.
- Invalid or unsupported format specifiers are marked `BAD_FORMAT` to avoid unsafe formatting.

## Test Signals

Validate on hardware with tracer registers. Enable `mlx5_fw` tracepoint, trigger firmware trace events, ownership changes, string DB updates, and core dumps. Test reload while traces arrive. Fault-inject PD/mkey/string DB/log buffer allocation failures. Verify devlink saved trace dumps and lost-event warnings under high trace rates.
