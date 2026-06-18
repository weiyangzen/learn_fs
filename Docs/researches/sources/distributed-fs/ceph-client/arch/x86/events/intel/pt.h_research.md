# sources/distributed-fs/ceph-client/arch/x86/events/intel/pt.h

## Purpose

`pt.h` defines the private data structures shared by the Intel Processor Trace perf PMU implementation. It models hardware ToPA entries, the global PT PMU capability cache, per-event AUX buffer bookkeeping, IP filter state, and per-CPU PT runtime context.

## Important APIs, Types, And Fields

`TOPA_PMI_MARGIN`, `TOPA_SHIFT`, and `sizes()` encode ToPA region sizing rules. `struct topa_entry` is the hardware table-entry layout with `end`, `intr`, `stop`, `size`, and physical `base` fields. `struct pt_pmu` wraps `struct pmu` and caches PT CPUID leaves, VMX compatibility, the Broadwell branch-enable quirk, and timing ratio data exported to userspace.

`struct pt_buffer` is the AUX-private buffer object used by `pt.c`: it owns the ToPA table list, first/last/current table pointers, current entry index, output offset, page count, logical head, data-size accumulator, snapshot/single/wrapped mode flags, STOP/INT marker state, and perf-provided data pages. `struct pt_filter` and `struct pt_filters` hold up to four address ranges mapped to RTIT address MSRs. `struct pt` is per-CPU state containing the perf output handle, the cached filters, NMI/pause/resume/VMX flags, and cached output MSR values.

## Control Flow

This header has no executable control flow beyond `sizes()`. Its fields are consumed by `pt.c` during PMU registration, event initialization, AUX setup, runtime trace start/stop, PMI handling, and address-filter synchronization.

## State And Persistence Behavior

The structures describe volatile kernel/perf state. `pt_buffer` persists for the lifetime of a perf AUX buffer and is freed through the PMU `free_aux` callback. `pt` persists per CPU while the driver is loaded. None of these structures write durable state; trace bytes live in perf AUX pages owned by perf core.

## Dependencies And Integration Points

The header depends on perf core types such as `struct pmu`, `struct perf_output_handle`, `local_t`, `local64_t`, `list_head`, and Intel PT capability constants. It is intentionally private to the Intel PT PMU driver and is included by `pt.c`.

## Risks And Edge Cases

Bitfield layout in `struct topa_entry` must match the Intel PT hardware format on the target compiler/ABI. Marker and pointer fields in `pt_buffer` are sensitive to wraparound and snapshot semantics. `PT_FILTERS_NUM` must remain aligned with hardware address-range capability handling in `pt.c`.

## Test Signals

Compile coverage for `pt.c`, perf PT AUX buffer tests, sysfs capability enumeration, and tracing on systems with and without multiple-entry ToPA are the main validation signals. Static checks should also catch structure-size assumptions such as the ToPA metadata fitting in a page.
