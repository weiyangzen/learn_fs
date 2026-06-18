<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-dtrace.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-dtrace.c

## Purpose
IPC3 firmware DMA trace support. It allocates host DMA trace buffers, exposes debugfs trace/filter files, starts/stops firmware trace DMA, handles position updates, drains trace data to userspace, and cleans up on suspend, crash, resume, and free.

## Important APIs, Types, and Functions
Defines `enum sof_dtrace_state` and `struct sof_dtrace_priv`. Filter helpers parse semicolon-separated entries into `sof_ipc_trace_filter_elem` arrays and send `SOF_IPC_TRACE_FILTER_UPDATE`. Trace buffer helpers include `sof_dtrace_set_host_offset()`, `sof_dtrace_avail()`, `sof_wait_dtrace_avail()`, `dfsentry_dtrace_read()`, `ipc3_dtrace_enable()`, `ipc3_dtrace_init()`, `ipc3_dtrace_posn_update()`, `ipc3_dtrace_fw_crashed()`, `ipc3_dtrace_release()`, `ipc3_dtrace_suspend()`, `ipc3_dtrace_resume()`, and `ipc3_dtrace_free()`. Ops are exported as `ipc3_dtrace_ops`.

## Control Flow, State, and Persistence
Initialization allocates a DMA page table and scatter-gather trace buffer, creates a compressed page table for firmware, creates debugfs entries on first boot, initializes a waitqueue, and sends trace DMA parameters to firmware. Enable chooses legacy or extended DMA params based on firmware ABI, initializes platform trace host resources, sends params, then starts host tracing. Firmware position messages atomically update `host_offset` and wake readers. Read wraps file position modulo buffer size, waits for available data, syncs DMA for CPU, and copies to user. Release/stop may send `TRACE_DMA_FREE` for ABI >= 3.20, stops host trace, marks draining, and wakes readers.

## Dependencies and Integration
Depends on debugfs, ALSA DMA buffer helpers, SOF page-table creation, platform trace callbacks from `ipc3-priv.h`, IPC no-reply sends, runtime PM and firmware boot for filter updates, and `ipc3.c` trace message dispatch.

## Risks and Test Signals
Risks include leaked `elems` on parse errors inside `trace_filter_parse()`, unbounded reader sleep until firmware position update or crash/stop, DMA coherency mistakes, ABI-specific free behavior, and races around trace state/host offset. Test signals are debugfs trace reads across buffer wrap, filter write parsing and rejection, suspend D0 versus deeper suspend, firmware crash waking readers with `-EIO`, ABI 3.7 extended params, ABI 3.20 DMA free, and overflow logging from position updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-dtrace.c -->
