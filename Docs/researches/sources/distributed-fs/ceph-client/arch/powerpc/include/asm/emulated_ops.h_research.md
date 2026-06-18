## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/emulated_ops.h

Purpose: tracks and reports software-emulated PowerPC operations and alignment faults.

Important APIs/types/functions: `struct ppc_emulated_entry`, global `ppc_emulated`, `ppc_warn_emulated`, `ppc_warn_emulated_print()`, `PPC_WARN_EMULATED()`, and `PPC_WARN_ALIGNMENT()`.

Control flow: emulation sites call macros that emit perf software events and, when stats are enabled, atomically increment the relevant counter and optionally print a warning.

State and persistence: optional global counters persist per emulated operation category. `ppc_warn_emulated` controls warning output.

Dependencies and integration: depends on atomics and perf events. Used by instruction emulation, alignment handling, math emulation, VSX/Altivec/SPE emulation, and PPC64 emulated instruction paths.

Risks and test signals: missing counters hide performance/debug signals; excessive warnings can flood logs. Test signals include perf emulation/alignment event counts, `/proc` or debug stats where exposed, alignment fault tests, and builds with each optional emulation feature.
