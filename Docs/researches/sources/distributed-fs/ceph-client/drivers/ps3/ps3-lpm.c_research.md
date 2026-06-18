# sources/distributed-fs/ceph-client/drivers/ps3/ps3-lpm.c

Purpose: PS3 Logical Performance Monitor driver. It exposes exported APIs for Cell performance counters, trace buffer copying, signal selection, bookmarks, and LPM lifecycle through LV1 hypervisor calls.

Important APIs/types/functions: `struct ps3_lpm_priv`, exported `ps3_set_bookmark()`, `ps3_set_pm_bookmark()`, counter read/write functions, `ps3_read_pm()`, `ps3_write_pm()`, `ps3_set_signal()`, `ps3_enable_pm()`, `ps3_disable_pm()`, trace-buffer copy helpers, interrupt helpers, `ps3_lpm_open()`, and `ps3_lpm_close()`.

Control flow: probe creates a singleton `lpm_priv` from PS3 system bus LPM descriptors. Consumers call `ps3_lpm_open()` to allocate or validate a 128-byte-aligned trace cache, construct an LV1 LPM instance, and initialize shadow registers. Counter and control APIs translate Linux/Cell PM abstractions into LV1 calls, using shadow registers for write-only PM control state. Signal selection translates island/group/bus encodings before `lv1_set_lpm_signal()`. Enabling PM optionally programs start/stop bookmark triggers, starts LPM, and writes a bookmark; disabling writes a stop bookmark, stops LPM, and records trace-buffer byte count. Copy helpers pull trace data through LV1 into kernel or user buffers.

State/dependencies: singleton global `lpm_priv`, atomic open flag enforcing one active LPM instance, LV1 ids/outlet, trace cache pointers, trace byte count, and shadow registers. Depends on PS3 LV1 calls, Cell PMU definitions, timebase, and PS3 system bus.

Risks: singleton design means exported APIs `BUG_ON()` if called before probe/open; remove calls `ps3_lpm_close()` unconditionally even if not open; many invalid parameters trigger `BUG()`; trace-buffer copy loops depend on hypervisor partial-copy behavior; user-copy helper can return partial data plus error; open rollback must free internal aligned buffer and decrement atomic flag.

Test signals: PS3 firmware probe, open/close with no trace buffer and aligned/unaligned buffers, counter size modes, PM control shadows, signal-group translation, enable/disable LPM, trace copy to kernel/user, removal after active open, and LV1 error propagation.
