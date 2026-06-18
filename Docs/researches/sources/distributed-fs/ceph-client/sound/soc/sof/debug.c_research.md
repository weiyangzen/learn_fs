# sources/distributed-fs/ceph-client/sound/soc/sof/debug.c

Purpose: SOF debugfs support for exposing DSP memory/register windows, firmware profile data, firmware state, memory usage, and exception/IPC dump handling.

Important APIs/types/functions: `snd_sof_debugfs_add_region_item_iomem()`, `snd_sof_debugfs_buf_item()`, `snd_sof_dbg_memory_info_init()`, `snd_sof_dbg_init()`, `snd_sof_free_debug()`, `snd_sof_dsp_dbg_dump()`, and `snd_sof_handle_fw_exception()`. Internal read paths include `sof_dfsentry_read()` and memory info IPC handling.

Control flow: debugfs reads validate position/count, align MMIO reads to 32-bit boundaries, optionally use cached buffers when debugfs cache is enabled and DSP is suspended, and copy data to userspace. `snd_sof_dbg_init()` creates `/sys/kernel/debug/sof`, exposes firmware/topology profile strings and IPC type, initializes the dfsentry list, adds platform debug regions, and exposes `fw_state`. Memory info lazily allocates a page buffer and sends a debug IPC after resuming/booting the DSP. Exception handling can retain D3 context, dumps IPC once, dumps DSP state once unless configured otherwise, and marks firmware trace crashed.

State and persistence: debugfs dentries hang off `sdev->debugfs_root`; entries are tracked in `sdev->dfsentry_list`. Optional cache buffers persist for D0-only windows. Dump suppression flags live in `sdev`.

Dependencies and integration points: Linux debugfs, runtime PM, SOF IPC debug memory command, platform debug maps, firmware trace crash handling, and platform-specific `ipc_dump`/`dbg_dump` ops.

Risks: debugfs may expose sensitive/register state and depends on correct access type. Reads while DSP is D3 are blocked unless cached/always-accessible. Memory info trusts firmware reply size after validation. D3 retention increments PM usage and must be balanced during remove.

Test signals: debugfs file creation/read in D0 and D3, memory_info IPC, firmware panic/IPC timeout logs, retained-context behavior, and debugfs cleanup on remove.
