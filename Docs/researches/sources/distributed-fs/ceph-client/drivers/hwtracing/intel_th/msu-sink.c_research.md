
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu-sink.c

Purpose: example pluggable MSU software sink buffer. It registers an `msu_buffer` named `sink` that allocates multiblock windows and immediately unlocks windows when notified ready, effectively discarding/looping trace data.

Important APIs/types/functions: `struct msu_sink_private` tracks device and a bounded table of SG tables. `msu_sink_assign()` forces `MSC_MODE_MULTI`. `msu_sink_alloc_window()` allocates coherent page-sized SG entries. `msu_sink_free_window()` frees them. `msu_sink_ready()` calls `intel_th_msc_window_unlock()`. `module_intel_th_msu_buffer(sink_mbuf)` registers with the MSU buffer registry.

Control flow: when users write `sink` to an MSC `mode` sysfs file, MSU calls assign, then allocates windows through the sink. During capture, when a window fills, MSU calls `ready()` and this sink returns the window to rotation without external processing.

State and persistence: per-assignment memory tracks up to `MAX_SGTS` SG tables. No persistent state or user-visible storage.

Dependencies and integration: depends on public `<linux/intel_th.h>` MSU buffer hooks, DMA coherent allocation, scatterlists, and the MSU driver's window-unlock export.

Risks: allocation error paths in `msu_sink_alloc_window()` do not free already allocated blocks on mid-loop failure, so this is best treated as example/test code. It assumes multiblock mode and bounded window count.

Test signals: load module, switch MSC mode to `sink`, allocate windows, enable tracing long enough to cycle windows, confirm no stop-on-full if IRQ/window unlock callbacks run.
