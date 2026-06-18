# sources/distributed-fs/ceph-client/arch/powerpc/perf/mpc7450-pmu.c

Purpose: processor PMU backend for 32-bit MPC7450-family PowerPC CPUs, translating perf events into MMCR0/MMCR1/MMCR2 settings and registering an early `power_pmu`.

Important APIs/types/functions: `mpc7450_pmu`, `init_mpc7450_pmu`, `mpc7450_classify_event`, `mpc7450_threshold_use`, `mpc7450_get_constraint`, `mpc7450_compute_mmcr`, `mpc7450_get_alternatives`, `mpc7450_disable_pmc`, and generic/cache event maps.

Control flow and state: event classification groups raw events by allowable PMC sets, from any PMC to fixed PMC. Constraint generation encodes required PMC/class use and shared threshold value/scale requirements. MMCR computation counts events by class, allocates PMCs from most constrained to least constrained using `classmap`, programs threshold fields into MMCR0/MMCR2, writes PMC selector fields into MMCR0 for PMC1-2 and MMCR1 for PMC3-6, and sets counter-enable bits.

State and persistence behavior: no persistent state. The file defines a static PMU descriptor and computes per-group register values. On 32-bit, it mirrors MMCR2 into `mmcra` because the architecture aliases `SPRN_MMCRA` to `SPRN_MMCR2`.

Dependencies and integration points: depends on PowerPC perf core `register_power_pmu`, PVR helpers for 7450/7455/7447/7447A/7448 detection, `struct mmcr_regs`, and generic perf hardware/cache event IDs. Registered with `early_initcall`.

Risks: class allocation and threshold sharing are hardware-specific; multiple threshold events must agree on threshold value/scale; invalid PMC selectors are rejected only through classification; 32-bit MMCRA alias behavior is easy to regress.

Test signals: build a 32-bit PowerPC kernel for supported CPUs; boot on MPC7450-family hardware/emulator; verify PMU registration, generic cycle/instruction/cache events, raw threshold events, conflict rejection for impossible groups, and PMC disable behavior.
