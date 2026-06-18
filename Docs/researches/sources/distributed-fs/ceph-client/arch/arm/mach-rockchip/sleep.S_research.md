# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/sleep.S

Purpose: Rockchip resume trampoline copied to SRAM for system suspend resume.

Important APIs/types/functions: `rockchip_slp_cpu_resume` is the executable resume entry; boot data globals include `rkpm_bootdata_l2ctlr_f`, `rkpm_bootdata_l2ctlr`, `rkpm_bootdata_cpusp`, `rkpm_bootdata_cpu_code`, and `rk3288_bootram_sz`.

Control flow: on resume it switches to SVC with interrupts/FIQs disabled, lets only CPU0 continue, optionally restores L2CTLR, loads saved stack pointer and CPU resume function pointer, then branches back into kernel resume code. Nonzero CPUs loop in WFE.

State and persistence: boot data words are filled by `pm.c` before suspend and consumed after resume from SRAM.

Dependencies and integration points: copied by RK3288 PM initialization and used by `cpu_suspend()` resume path.

Risks: incorrect boot data or SRAM copy causes resume hang. Only CPU0 resume is supported here; secondary CPUs must be re-managed elsewhere.

Test signals: RK3288 suspend/resume, L2CTLR restore validation, and bootram size consistency with copied code.
