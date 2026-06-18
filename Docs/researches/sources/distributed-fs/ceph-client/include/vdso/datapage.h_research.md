<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/datapage.h -->
# sources/distributed-fs/ceph-client/include/vdso/datapage.h

Purpose: defines the shared VVAR/vDSO data page layout for fast userspace time and getrandom support, including clock data, timestamps, namespace offsets, RNG state, architecture data, symbols, and page offsets.

Important APIs and types: `vdso_timestamp`, `vdso_clock`, `vdso_time_data`, and `vdso_rng_data` are the core shared layouts. Macros define accelerated clock masks (`VDSO_HRES`, `VDSO_COARSE`, `VDSO_RAW`, `VDSO_AUX`), clocksource slots, architecture data size/pages, VVAR symbols, and `enum vdso_pages` offsets. Optional arch structs come from `asm/vdso/time_data.h` and `asm/vdso/arch_data.h`.

Control flow: kernel timekeeping writes VVAR data under sequence counters; userspace vDSO code reads `vdso_u_time_data`, checks clock mode/seq, computes time from `cycle_last`, `mult`, `shift`, `mask`, and `basetime`, or follows time namespace offsets. getrandom vDSO code reads `vdso_u_rng_data` generation/readiness. Assembly linker scripts use `VDSO_VVAR_SYMS` to publish hidden VVAR symbols.

State and persistence: this is live shared kernel-to-userspace state: sequence counters, clocksource parameters, basetimes, namespace offsets, timezone/resolution, RNG generation/readiness, and arch data. It is not persistent across boot but is ABI-sensitive for 64-bit and compat readers.

Dependencies and integration points: depends on Linux/UAPI types, time definitions, bits, alignment, cache, page, and optional arch data. It integrates with kernel timekeeping, vDSO clock_gettime/gettimeofday/time, time namespaces, vDSO getrandom, linker scripts, and architecture-specific vDSO implementations.

Risks and test signals: high risks include struct layout changes affecting compat vDSO, sequence counter ordering, cacheline placement, time namespace slow-path markers, VVAR page offset changes, and hidden symbol relocation. Test vDSO time under concurrent updates, time namespaces, 32-bit compat, getrandom readiness/reseed, linker symbol placement, and all arch configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/datapage.h -->
