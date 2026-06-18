# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nmi.h

Purpose: declares PowerPC NMI/watchdog hooks and hypervisor nonrecoverable NMI checking.

Important APIs/types/functions: with `CONFIG_PPC_WATCHDOG`, declares `soft_nmi_interrupt(struct pt_regs *regs)` and `watchdog_hardlockup_set_timeout_pct(u64 pct)`; otherwise the timeout setter is a no-op. `hv_nmi_check_nonrecoverable(struct pt_regs *regs)` is always declared.

Control flow: watchdog/NMI exception code calls the soft NMI handler and hypervisor nonrecoverable checker from NMI context.

State and persistence: watchdog timeout percentage is maintained by implementation; this header has no storage.

Dependencies and integration points: integrates PowerPC exception code, hardlockup watchdog, and hypervisor NMI handling.

Risks: NMI context has severe locking and reentrancy constraints. Disabled watchdog builds must not assume `soft_nmi_interrupt` exists.

Test signals: hardlockup watchdog tests, injected soft NMI paths, hypervisor nonrecoverable NMI handling, and builds with/without `CONFIG_PPC_WATCHDOG`.
