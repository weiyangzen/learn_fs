# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/mmap.c

Purpose: verifies perf ring-buffer and AUX mappings cannot be partially punched, overwritten, or invalidly remapped in ways that break perf VMA invariants.

Important APIs/types/functions: fixture `perf_mmap` owns a perf fd, mapped pointer, and reserved address region. Variants `rb` and `aux` cover base ring buffer and AUX buffer. `read_event_type()` reads PMU type IDs from `/sys/bus/event_source/devices/*/type`.

Control flow: setup reserves a PROT_NONE region, scans event sources for a `perf_event_open()` target that can be mmaped, optionally checks AUX support by setting `perf_event_mmap_page.aux_offset/aux_size`, then opens a final fd and maps the selected buffer at fixed addresses. Tests try invalid `mremap()` splits, valid whole remap, invalid `munmap()` holes, and invalid anonymous `MAP_FIXED` overlays.

State and persistence: creates perf fds and process mappings only; teardown unmaps the whole reserved region and closes the fd.

Dependencies/integration: requires sysfs event source directory, `perf_event_open`, mmapable event, and for AUX variant an AUX-capable PMU. Permission failures produce skip.

Risks: availability is platform-dependent. Pointer arithmetic on `void *` relies on GNU C. Fixed mapping behavior is sensitive to kernel VMA semantics being tested.

Test signals: setup skips with `perf not available`, `No mappable perf event found`, `No permissions`, or `No AUX event found`; assertions fail on unexpected mapping/remap/unmap behavior.
