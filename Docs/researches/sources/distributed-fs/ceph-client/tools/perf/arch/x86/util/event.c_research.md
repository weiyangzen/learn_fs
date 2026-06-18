# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/event.c

Purpose: This x86-64 utility synthesizes extra kernel mmap events for perf sessions. It emits `PERF_RECORD_MMAP` records for special kernel maps so tools can resolve symbols beyond the primary kernel map.

Important APIs, types, and functions: The implementation is compiled only under `__x86_64__`. `struct perf_event__synthesize_extra_kmaps_cb_args` carries the perf tool, callback, machine, and reusable event buffer. `perf_event__synthesize_extra_kmaps_cb()` formats one synthetic mmap record for maps accepted by `__map__is_extra_kernel_map()`. `perf_event__synthesize_extra_kmaps()` allocates the event buffer, iterates kernel maps via `maps__for_each_map()`, and frees the buffer.

Control flow: The public function gets `machine__kernel_maps(machine)`, allocates enough space for an mmap event plus ID header, then iterates maps. The callback skips non-extra maps, computes record size from filename length and `machine->id_hdr_size`, zeroes the buffer, fills header type/size/misc, start/len/pgoff/pid, copies the kmap name, and sends the event to `perf_tool__process_synth_event()`.

State and persistence: State is transient. The function reuses one allocated union event buffer while iterating maps and emits synthesized events into the current perf processing pipeline. It does not alter the map structures.

Dependencies and integration points: It overrides the weak generic `perf_event__synthesize_extra_kmaps()` used by `util/synthetic-events.c`. It depends on `machine`, `maps`, `map`, `kmap`, `perf_tool`, and synthetic event processing APIs. The host-vs-guest distinction controls `PERF_RECORD_MISC_KERNEL` versus `PERF_RECORD_MISC_GUEST_KERNEL`.

Risks: Incorrect size calculation can corrupt synthetic event processing because the filename has variable aligned length plus optional ID header. The x86-64 guard means 32-bit builds use generic behavior. Misclassifying extra kernel maps would either omit useful symbol coverage or emit duplicate/confusing mmap records.

Test signals: Perf sessions on x86-64 with extra kernel maps should include synthetic mmap records with correct kernel/guest misc flags and filenames. Symbol-resolution tests or verbose synthetic-event traces can reveal missing extra maps.
