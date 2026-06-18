# Group Research: group_422_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_subr_bus_c_sources_o_2696fb227ed6

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_bus.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_bus.c

## Purpose
Implements FreeBSD's core kernel newbus framework: devclasses, devices, driver registration, probing/attachment, generic bus methods, resource-list helpers, root bus setup, device-tree sysctls, `/dev/devctl2` control operations, device path caching, device properties, and obsolete-feature diagnostics.

## Main Elements
- Core data structures:
  - `struct driverlink`: driver registration entry, bus pass, and deferred-probe flag.
  - `struct devclass`: driver list, parent class, unit-indexed device table, and devclass sysctl tree.
  - `struct _device`: kobj-backed device node with parent/children, driver/devclass/unit, state, flags, ivars, softc, properties, and sysctl state.
  - `struct device_prop_elm`: named per-device property with optional destructor.
- Topology and pass control:
  - `bus_topo_lock()`, `bus_topo_unlock()`, `bus_topo_assert()` currently use Giant.
  - `bus_get_pass()` and `bus_set_pass()` advance boot-time driver pass levels and trigger `BUS_NEW_PASS(root_bus)`.
  - `driver_register_pass()` tracks distinct bus pass levels.
- Devclass management:
  - `devclass_create()`, `devclass_find()`, parent-class inheritance, driver add/delete/quiesce, device table allocation, unit reservation, device and driver enumeration.
  - `devclass_driver_added()` recursively notifies matching buses when a driver appears.
  - `devclass_driver_deleted()` detaches matching devices when a driver is removed.
- Device lifecycle:
  - `device_add_child[_ordered]()`, `device_delete_child()`, `device_delete_children()`, and `device_find_child()`.
  - `device_probe_child()`, `device_probe()`, `device_probe_and_attach()`, `device_attach()`, `device_detach()`, `device_quiesce()`, `device_shutdown()`.
  - Driver selection probes candidate drivers in devclass and parent-devclass lists, honors bus pass levels and wildcard/fixed devclasses, and uses probe return priority.
  - Failed attach can either reset probe state for future retries or leave the device disabled when `hw.bus.disable_failed_devices` is set.
- Device attributes:
  - Getters for parent, children, driver, devclass, name/unit, description, flags, softc, ivars, state, quiet/enabled/alive/attached/suspended status.
  - Setters for description, flags, softc ownership, ivars, devclass, fixed devclass, driver, and unit.
  - Busy recursion via `device_busy()` / `device_unbusy()`.
- Resource helpers:
  - `resource_init_map_request_impl()` and `resource_validate_map_request()` normalize and bounds-check resource map requests.
  - `resource_list_*()` manages child resource entries, reserved resources, active-resource release, unreserve, printing, and purge.
  - `bus_generic_*()` provides generic child attach/detach/suspend/resume/reset, ivar, property, interrupt, resource, CPU set, DMA tag, bus tag, domain, path, and rescan behavior.
  - `bus_generic_rl_*()` implements resource-list-backed bus resource operations.
  - `bus_generic_rman_*()` implements rman-backed allocation, adjustment, release, activation, mapping, IRQ activation, and deactivation.
  - Public `bus_*()` wrappers delegate to parent bus methods for resources, interrupts, CPU sets, DMA tags, bus tags, domains, child pnp/location info, and presence.
- Root bus and module integration:
  - `root_bus_module_handler()` initializes global device list, creates `root0`, installs root driver, and initializes `devctl2`.
  - `root_bus_configure()` advances to `BUS_PASS_DEFAULT`.
  - `driver_module_handler()` handles driver module load, unload, and quiesce.
  - `bus_enumerate_hinted_children()` walks loader hints for bus-specific and generic child declarations.
- User/kernel introspection and control:
  - `hw.bus.info` and `hw.bus.devices` sysctls expose generation and flat device records.
  - `bus_data_generation_check()` / `bus_data_generation_update()` track device-tree changes.
  - `device_lookup_by_name()` and `find_device()` support direct lookup and `dev_lookup` event handlers.
  - `/dev/devctl2` ioctl handler supports attach, detach, enable, disable, suspend, resume, set/clear driver, rescan, delete, freeze/thaw, reset, and get path.
  - Freeze/thaw defers probe and nomatch actions until `device_do_deferred_actions()`.
- Device path and properties:
  - `device_get_path()` and `bus_generic_get_device_path()` construct locator paths, including FreeBSD-style `/nameunit` paths.
  - `dev_wired_cache_*()` caches locator/path strings for matching wired devices against `at` hints.
  - `device_set_prop()`, `device_get_prop()`, `device_clear_prop()`, `device_clear_prop_alldev()` manage named properties with destructors.
- Diagnostics:
  - BUS_DEBUG print functions dump devices, drivers, devclasses, and trees.
  - `_gone_in()` and `_gone_in_dev()` print or panic for deprecated/obsolete APIs depending on `debug.obsolete_panic`.
  - DDB commands show a specific device or all devices.

## Dependencies And Integration
This file is central to kernel driver infrastructure. It depends on kobj, module loading, sysctl, rman, resource hints, eventhandlers, taskqueue, VNET checks, random harvesting, domainset allocation, IOMMU property reporting, optional INTRNG IRQ hooks, and DDB. It provides the implementation behind many `<sys/bus.h>` APIs used by bus and device drivers.

## Risk Notes
This file is concurrency- and state-sensitive. Many operations require the bus topology lock, but the lock is currently Giant, so incorrect future locking changes could expose races. Probe/attach/detach state transitions must keep devclass tables, sysctls, softc ownership, driver kobj state, resource ownership, and user-visible generation counts consistent. `/dev/devctl2` is privileged and mutates live device topology; incorrect validation can detach, delete, or rebind active devices. Resource-list reserved/allocation flags are subtle and can leak or double-release resources if bus drivers misuse them.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_bus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_bus_dma.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_bus_dma.c

## Purpose
Provides common MI busdma helper code for locking, loading different memory descriptions into DMA maps, DMA template construction, crypto-buffer loading, and no-IOMMU fallback stubs.

## Main Elements
- `busdma_lock_mutex()`: adapts a mutex to `BUS_DMA_LOCK` / `BUS_DMA_UNLOCK`.
- `_busdma_dflt_lock()`: panic stub used when deferred DMA callbacks are impossible but a default lock is invoked.
- Internal loaders:
  - `_bus_dmamap_load_vlist()` loads virtual segment lists with offset/length clipping.
  - `_bus_dmamap_load_plist()` loads physical segment lists.
  - `_bus_dmamap_load_mbuf_epg()` handles unmapped external-page mbufs, including header, page array, and trailer.
  - `_bus_dmamap_load_single_mbuf()` and `_bus_dmamap_load_mbuf_sg()` load mbufs and chains.
  - `_bus_dmamap_load_uio()` loads user or kernel `uio` vectors using the correct pmap.
- Public load APIs:
  - `bus_dmamap_load()`, `bus_dmamap_load_mbuf()`, `bus_dmamap_load_mbuf_sg()`, `bus_dmamap_load_uio()`, `bus_dmamap_load_bio()`, `bus_dmamap_load_mem()`.
  - `bus_dmamap_load_ma_triv()` loads arrays of VM pages through physical addresses.
  - `bus_dmamap_load_crp_buffer()` and `bus_dmamap_load_crp()` load OpenCrypto buffers.
- Template helpers:
  - `bus_dma_template_init()` fills default tag constraints.
  - `bus_dma_template_fill()` applies keyed parameter overrides.
  - `bus_dma_template_tag()` creates a real DMA tag from the template.
- No-IOMMU compatibility:
  - `bus_dma_iommu_set_buswide()` returns false.
  - `bus_dma_iommu_load_ident()` returns success without doing work.

## Dependencies And Integration
Relies on machine-dependent busdma backends for `_bus_dmamap_load_buffer()`, `_bus_dmamap_load_phys()`, `_bus_dmamap_complete()`, `_bus_dmamap_waitok()`, `_bus_dmamap_load_ma()`, and optional KMSAN hooks. Integrates with mbufs, VM pages, `memdesc`, BIO, UIO, pmap, OpenCrypto, and `bus_dma_tag_create()`.

## Risk Notes
Segment counting uses the busdma convention of starting at `-1` and incrementing after load completion, which is easy to misuse. NOWAIT versus WAITOK controls callback deferral and `EINPROGRESS` behavior. Extended-page mbufs require careful offset arithmetic across headers, physical pages, and trailers. The default lock stub is intentionally fatal because deferred callbacks without a valid driver lock are a driver bug.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_bus_dma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_busdma_bounce.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_busdma_bounce.c

## Purpose
Common busdma bounce-page management code included by busdma backends that need low-address/alignment-safe DMA buffers.

## Main Elements
- `struct bounce_page`: tracks bounce KVA, bus address, original data address/page/offset/count, and queue linkage.
- `struct bounce_zone`: groups bounce pages by low-address, alignment, optional NUMA domain, counters, waiting maps, and sysctl tree.
- Global state:
  - `bounce_lock`, total page counters, zone list, deferred callback list, and `hw.busdma.total_bpages`.
- Reservation and allocation:
  - `_bus_dmamap_reserve_pages()` reserves pages or queues WAITOK maps for deferred retry.
  - `alloc_bounce_zone()` reuses or creates a suitable zone, exports per-zone sysctls, and starts the `busdma` kernel thread.
  - `alloc_bounce_pages()` allocates contiguous bounce pages under the zone's low-address and alignment constraints.
  - `reserve_bounce_pages()` updates free/reserved counts and per-map reservations.
- Address and segment helpers:
  - `addr_needs_bounce()` tests lowaddr/highaddr exclusion and alignment.
  - `add_bounce_page()` consumes a reserved page, records original data mapping, optionally preserves page offset, and returns the bounce bus address.
  - `_bus_dmamap_addseg()` and `_bus_dmamap_addsegs()` coalesce or split DMA segments under boundary, max segment, and segment-count constraints.
- Cleanup and deferral:
  - `free_bounce_pages()` returns active pages, wakes queued maps whose reservations can now be satisfied, and schedules callbacks.
  - `busdma_thread()` runs deferred loads under the driver's DMA lock and accounts deferred time.

## Dependencies And Integration
This file is designed to be included into architecture-specific busdma implementations, not compiled alone. It assumes `M_BUSDMA`, `struct bus_dmamap`, `hw_busdma`, DMA-tag field macros, optional domain macros, and backend load/sync code are already available.

## Risk Notes
Bounce accounting must keep `free_bpages`, `reserved_bpages`, `active_bpages`, and per-map `pagesneeded/pagesreserved` consistent under `bounce_lock`. WAITOK deferral re-enters `bus_dmamap_load_mem()` from a kernel thread while holding the driver lock, so incorrect lock callbacks can deadlock. `BUS_DMA_KEEP_PG_OFFSET` mutates bounce page virtual/bus addresses temporarily and must reset them on free.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_busdma_bounce.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_busdma_bufalloc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_busdma_bufalloc.c

## Purpose
Provides UMA-backed buffer allocation pools for busdma memory allocation paths, plus optional uncacheable allocation hooks.

## Main Elements
- `struct busdma_bufalloc`: stores minimum allocation size and a fixed array of size-class zones.
- `busdma_bufalloc_create()`: creates power-of-two UMA zones from at least 32 bytes up to `PAGE_SIZE`, with each zone aligned to its size and optional custom slab alloc/free functions.
- `busdma_bufalloc_destroy()`: destroys all created UMA zones and frees the allocator.
- `busdma_bufalloc_findzone()`: finds the smallest zone able to satisfy a requested size, or returns NULL for larger-than-page allocations.
- `busdma_bufalloc_alloc_uncacheable()` / `busdma_bufalloc_free_uncacheable()`: allocate/free uncacheable memory with `kmem_alloc_attr_domainset()` when `VM_MEMATTR_UNCACHEABLE` is available.

## Dependencies And Integration
Used by busdma backends implementing `bus_dmamem_alloc()`. Depends on UMA, VM kernel allocation, domainsets, busdma buffer-zone definitions, and `M_DEVBUF`.

## Risk Notes
The fixed 12-zone array assumes `PAGE_SIZE <= 65536`; larger pages intentionally fail compilation. UMA contiguity is only guaranteed up to a page, so larger allocations must use page-oriented allocators. Uncacheable allocation panics if the platform lacks `VM_MEMATTR_UNCACHEABLE`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_busdma_bufalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_capability.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_capability.c

## Purpose
Implements Capsicum capability-rights manipulation helpers shared by the kernel and libc.

## Main Elements
- Kernel-only exported constant rights objects, such as `cap_read_rights`, `cap_write_rights`, `cap_ioctl_rights`, socket rights, pathname-operation rights, and `cap_no_rights`.
- `right_to_index()`: maps a right's encoded index bit to the corresponding `cap_rights_t` array slot.
- Varargs helpers:
  - `cap_rights_vset()` ORs rights into a rights set.
  - `cap_rights_vclear()` clears rights while preserving index/version bits.
  - `cap_rights_is_vset()` checks whether all requested rights are present.
- Public APIs:
  - `__cap_rights_init()`, `__cap_rights_set()`, `__cap_rights_clear()`, `__cap_rights_is_set()`.
  - `cap_rights_is_empty()` and `cap_rights_is_valid()`.
  - `cap_rights_merge()`, `cap_rights_remove()`, and userland `cap_rights_contains()`.

## Dependencies And Integration
Includes `<sys/capsicum.h>` and is compiled in both kernel and libc contexts. Kernel builds map `assert()` to `KASSERT()` and export preinitialized common rights values.

## Risk Notes
The rights representation encodes version, array size, and index bits inside each slot, so all bit operations must preserve metadata while modifying only rights bits. Varargs lists are terminated by a zero right; missing termination would read past arguments. Validation is strict about version, array size, index-slot consistency, and containment within all valid rights.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_capability.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_clock.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_clock.c

## Purpose
Provides generic kernel conversions between POSIX `timespec`, binary `clocktime`, and BCD RTC clock formats, plus clock debugging and UTC-offset sysctl support.

## Main Elements
- Sysctls:
  - `machdep.adjkerntz`: local UTC offset in seconds; writes call `resettodr()`.
  - `debug.clocktime`: enables conversion debug printing.
  - `machdep.wall_cmos_clock`: controls whether `utc_offset()` returns `adjkerntz`.
- Calendar helpers:
  - Leap-year, days-per-month/year, day-of-week, and a precomputed 2017 day-count base for faster conversions.
  - `nsdivisors[]` supports fractional-second printing with 0-9 digits.
- Conversion APIs:
  - `clock_ct_to_ts()` converts `struct clocktime` to `timespec`, including 2-digit RTC year pivoting.
  - `clock_bcd_to_ts()` validates BCD fields, converts to binary, handles optional AM/PM mode, then calls `clock_ct_to_ts()`.
  - `clock_ts_to_ct()` converts seconds since 1970 to calendar fields and weekday.
  - `clock_ts_to_bcd()` converts `timespec` to BCD RTC fields with optional AM/PM mode.
- Printing helpers:
  - `clock_print_bcd()`, `clock_print_ct()`, `clock_print_ts()`.
- `utc_offset()`: returns local offset only when wall CMOS clock mode is enabled.

## Dependencies And Integration
Used by RTC and platform clock drivers through `<sys/clock.h>`. Depends on kernel sysctl, timecounter definitions, BCD macros, and `resettodr()`.

## Risk Notes
`clock_ct_to_ts()` rejects invalid calendar fields and protects 32-bit `time_t` from post-2037 overflow. BCD inputs are validated before conversion to avoid assertions. Leap seconds are not fully modeled: input seconds above 59 are rejected in `clock_ct_to_ts()`, while `clock_ts_to_ct()` permits an asserted range up to 60.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_clockcalib.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_clockcalib.c

## Purpose
Calibrates an arbitrary hardware clock function against the current best timecounter using online statistical regression.

## Main Elements
- `clockcalib()`: samples the target clock and reference timecounter, computes running means, variances, and covariance, and returns the inferred target frequency.
- Handles wrapping of the reference timecounter by tracking an accumulated adjustment.
- Uses a 1 PPM uncertainty target and only accepts calibration after the uncertainty condition remains true for more than half the collected samples.
- Falls back to a slower direct ratio estimate if calibration takes more than one reference-clock second.
- Adds a decreasing variable spin delay to reduce aliasing risk between the sampling loop and reference clock.

## Dependencies And Integration
Uses the global `timecounter`, `tc_get_timecount()`, `tc_counter_mask`, `tc_frequency`, `cpu_spinwait()`, and TSLOG enter/exit instrumentation. Intended for early or low-level clock frequency calibration.

## Risk Notes
The method assumes both clocks tick at stable rates during sampling. If they vary, the function prints a warning and falls back. The implementation intentionally uses floating-point statistical calculations in kernel code, so architecture/kernel FP constraints matter for integration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_clockcalib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_compressor.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_compressor.c

## Purpose
Provides a small pluggable compressor interface used for compressed user and kernel core dumps.

## Main Elements
- Framework:
  - `struct compressor_methods`: format, init, reset, write, fini methods.
  - `struct compressor`: selected methods, private stream, output callback, and callback argument.
  - `DATA_SET(compressors, ...)` registers built-in formats.
  - `compressor_avail()`, `compressor_init()`, `compressor_format()`, `compressor_reset()`, `compressor_write()`, `compressor_flush()`, `compressor_fini()`.
- Gzip backend under `GZIO`:
  - `gz_stream` stores output buffer, offset, CRC, and zlib state.
  - `gz_init()` clamps compression level and initializes raw deflate.
  - `gz_reset()` emits a gzip header into the output buffer.
  - `gz_write()` streams input, updates CRC, flushes full buffers via callback, and appends gzip trailer on finish.
  - `gz_fini()` ends zlib and frees buffers.
- Zstd backend under `ZSTDIO`:
  - `zstdio_stream` stores static zstd context, input/output buffers, offset, and workspace.
  - `zstdio_init()` allocates M_NODUMP workspace and buffer, enables checksum, and sets compression level.
  - `zstdio_reset()` resets the zstd session and unknown source size.
  - `zst_flush_intermediate()` writes full output blocks, bounded by `maxiosize`.
  - `zstdio_flush()` finalizes the stream and writes remaining partial output.
  - `zstdio_write()` streams data and detects lack of forward progress.
  - `zstdio_fini()` frees workspace, buffer, and stream.

## Dependencies And Integration
Uses compile-time options `opt_gzio.h` and `opt_zstdio.h`, zlib, zstd, linker sets, kernel malloc, endian helpers, and `M_NODUMP` to avoid including compressor state in dumps being compressed.

## Risk Notes
The callback is the only output path, so errors must propagate immediately. Gzip manually constructs headers/trailers and tracks stream offset and CRC. Zstd protects against no-forward-progress loops and emits full blocks before final partial output. `compressor_fini()` calls the backend finalizer for private state; callers must follow the surrounding API contract for the wrapper object lifetime.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_compressor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_counter.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_counter.c

## Purpose
Implements MI wrappers and sysctl handlers for per-CPU 64-bit counters, plus an MP-friendly rate-check helper built on counters.

## Main Elements
- Counter allocation and access:
  - `counter_u64_alloc()`, `counter_u64_free()`, `counter_u64_zero()`, `counter_u64_fetch()`.
  - Uses `pcpu_zone_8` per-CPU UMA storage.
- Sysctl handlers:
  - `sysctl_handle_counter_u64()` exports a single counter and zeros it on any write attempt.
  - `sysctl_handle_counter_u64_array()` exports an array of counters and zeros all counters on write.
- Rate limiting:
  - `struct counter_rate`: event counter, reset lock, last tick, over-limit state, and period.
  - `counter_rate_alloc()` / `counter_rate_free()`.
  - `counter_rate_get()` returns current count or zero if the period has expired.
  - `counter_ratecheck()` increments the counter and returns 0, -1, or the previous over-limit count depending on rate state.
- Sysinit helpers:
  - `counter_u64_sysinit()` and `counter_u64_sysuninit()` allocate/free counters referenced by static initializers.

## Dependencies And Integration
Depends on per-CPU UMA zones, `<sys/counter.h>` inline primitives, kernel ticks/hz, atomics, sysctl, and malloc type `M_COUNTER_RATE`.

## Risk Notes
`counter_ratecheck()` intentionally avoids a heavyweight lock but can skip updates when another thread is resetting the counter. The code uses both `ticks` and `tick` names in rate age checks, so correctness depends on the intended kernel globals/macros. Sysctl writes have destructive semantics: any write zeros the exported counter or array.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_counter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_coverage.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_coverage.c

## Purpose
Provides compiler sanitizer coverage entry points for kernel coverage/fuzzing instrumentation and dynamic registration of coverage callbacks.

## Main Elements
- Callback registration:
  - `cov_register_pc()` / `cov_unregister_pc()` install or clear the PC tracing callback.
  - `cov_register_cmp()` / `cov_unregister_cmp()` install or clear the comparison tracing callback.
- Sanitizer coverage hooks:
  - `__sanitizer_cov_trace_pc()` records the caller return address through `cov_trace_pc`.
  - `__sanitizer_cov_trace_cmp1/2/4/8()` records non-constant comparisons with size tags.
  - `__sanitizer_cov_trace_const_cmp1/2/4/8()` records constant comparisons with `COV_CMP_CONST`.
  - `__sanitizer_cov_trace_switch()` decodes sanitizer switch metadata and emits comparison records for each case.
- Callback pointers are read and written with atomic pointer operations.

## Dependencies And Integration
Uses `<sys/coverage.h>` callback types and comparison flag macros. Built to satisfy compiler-inserted sanitizer coverage calls, optionally defining `SAN_RUNTIME` when interceptors are needed.

## Risk Notes
These hooks may execute at very high frequency, so the fast path is minimal: atomic callback load and NULL check. Callback implementations must tolerate arbitrary instrumented call sites. `__sanitizer_cov_trace_switch()` trusts the compiler-provided case array layout and rejects unsupported operand sizes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_coverage.c -->