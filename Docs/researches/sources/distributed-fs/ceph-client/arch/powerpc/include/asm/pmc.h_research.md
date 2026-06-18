# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmc.h

Purpose: This header provides the architecture interface for reserving and enabling PowerPC performance monitor counters and for coordinating PMU ownership with pseries/LPAR and KVM HV state.

Important APIs/types/functions: `perf_irq_t` is a callback taking `struct pt_regs *`; `perf_irq` is the registered interrupt handler pointer. `reserve_pmc_hardware`, `release_pmc_hardware`, and `ppc_enable_pmcs` form the generic PMU reservation and enable API. On Book3S 64-bit, `ppc_set_pmu_inuse` updates lppaca and/or paca state so firmware or KVM can know PMU registers are in use. `ppc_get_pmu_inuse` exists for KVM HV builds, and `power4_enable_pmcs` is declared for POWER4-style PMU enablement.

Control flow: Perf or low-level PMU code reserves hardware with a new interrupt handler, enables PMCs, handles PMU interrupts through `perf_irq`, and releases the reservation on teardown. On LPAR systems or KVM HV capable builds, the reservation path can mark PMU usage in per-CPU/shared processor accounting structures.

State and persistence: The main persistent state is the global `perf_irq` pointer and per-CPU/per-partition PMU-in-use flags in `lppaca` and `paca`. The header itself has no storage, but its inline setter mutates firmware-visible and hypervisor-visible state.

Dependencies and integration points: It includes `asm/ptrace.h` for interrupt register context. Book3S 64-bit paths depend on `lppaca`, `paca`, and `firmware_has_feature(FW_FEATURE_LPAR)`. It integrates with perf, PMU interrupt handlers, pseries shared processor firmware, and KVM HV virtualization.

Risks and test signals: Reservation must serialize users so two PMU clients do not install competing handlers. PMU-in-use state must be set and cleared around guest and host PMU access to avoid corrupting counters or exposing stale state. Tests should cover perf event setup/teardown, nested KVM/pseries builds, LPAR and bare-metal builds, and PMU interrupt delivery with `pt_regs` content.
