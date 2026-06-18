# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/inc/dmub_trace_buffer.h

## Purpose

`dmub_trace_buffer.h` defines a compact firmware trace-buffer format for DMCUB/DMUB. It provides trace event codes for boot, PHY initialization, firmware loading, idle, performance tracing, and power-gating completion, plus a fixed-size buffer layout that the driver can parse after firmware writes trace entries.

## Important APIs, Types, And Constants

The header includes `dmub_cmd.h`, so it inherits the fixed-width types used by the broader DMUB ABI. `LOAD_DMCU_FW` and `LOAD_PHY_FW` identify firmware load categories.

`enum dmucb_trace_code` contains event identifiers such as `DMCUB__MAIN_BEGIN`, PHY init/load start/end states, DMCU ERAM/ISR load start/end states, `DMCUB__MAIN_IDLE`, `DMCUB__PERF_TRACE`, and `DMCUB__PG_DONE`.

`struct dmcub_trace_buf_entry` contains a trace code, a tick count, and two event-specific 32-bit parameters. `TRACE_BUF_SIZE` is fixed at 1024 bytes. `PERF_TRACE_MAX_ENTRY` computes the number of entries after an 8-byte buffer header. `struct dmcub_trace_buf` stores `entry_count`, `clk_freq`, and the trace entries.

## Control Flow And Data Flow

Firmware writes entries into the trace buffer as boot and runtime milestones occur. Driver-side diagnostic code can map or copy the buffer, interpret `entry_count` and `clk_freq`, and convert each entry's tick count into timing information. The event code selects how to interpret `param0` and `param1`.

## State And Persistence Behavior

The buffer is a persistent diagnostic memory region across the firmware session. It is bounded to 1 KiB and does not include locking or wrap semantics in this header. Consumers must treat `entry_count` as firmware-owned and validate it against `PERF_TRACE_MAX_ENTRY`.

## Dependencies And Integration Points

This header integrates with DMUB firmware diagnostics, `dmub_cmd.h` trace entry definitions, the DMUB service trace/outbox paths, and any driver debugfs or timeout reporting code that dumps DMCUB trace data. It must stay layout-compatible with firmware trace writers.

## Risks And Edge Cases

The enum name is `dmucb_trace_code`, while most of the subsystem uses DMUB/DMCUB naming, so searchability can be uneven. `entry_count` can be corrupt or firmware-controlled, so readers should clamp it. The fixed 1 KiB size limits trace depth and makes event loss possible during long boot/runtime sequences.

## Test Signals

Test signals include nonzero `entry_count` after firmware boot, expected begin/end event ordering for PHY and DMCU loads, plausible `tick_count` deltas when `clk_freq` is set, and correct behavior when the buffer is empty or full. Timeout diagnostics should include these entries when firmware hangs during boot or PHY initialization.
