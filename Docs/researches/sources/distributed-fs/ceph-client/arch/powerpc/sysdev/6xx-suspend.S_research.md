<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/6xx-suspend.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/6xx-suspend.S

Purpose: low-level standby entry/return routine for Book3S 32-bit 6xx-style processors whose HID0 sleep state resumes without reset.

Important APIs/types/functions: global `mpc6xx_enter_standby` and local `ret_from_standby`. It manipulates `SPRN_HID0`, MSR `EE` and `POW`, thread-info local flags, and the link register.

Control flow: saves LR, clears HID0 doze/nap, sets HID0 sleep, points LR at `ret_from_standby`, marks `_TLF_SLEEPING`, enables interrupts and power management in MSR, syncs, writes MSR, and spins. On interrupt wake, execution resumes at `ret_from_standby`, clears HID0 sleep, restores LR, and returns.

State and persistence: persists sleep intent in HID0 and thread local flags while the CPU sleeps. No memory allocation or device state is touched.

Dependencies and integration points: built only for suspend on `PPC_BOOK3S_32`. It depends on assembly offsets for `TI_LOCAL_FLAGS`, HID0 bit definitions, and platform suspend code calling the symbol.

Risks: incorrect MSR/HID0 ordering can leave the CPU awake, stuck asleep, or with interrupts misconfigured. The infinite loop is expected to be escaped only by the processor wake path.

Test signals: standby/resume on 6xx-compatible systems, HID0 sleep bit clearing after wake, and no corruption of LR/thread flags validate the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/6xx-suspend.S -->
