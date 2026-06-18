<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive.h

Purpose: Declares the main PowerPC XIVE interrupt-controller software interface and KVM/native queue APIs.

Important APIs/types/functions: `xive_tima`, `xive_tima_os`, `xive_tima_offset`, `struct xive_irq_data`, XIVE IRQ flags, `struct xive_q`, `xive_enabled()`, init/SMP/teardown helpers, xmon dump helpers, and native VP/IRQ/queue configuration and state APIs.

Control flow: Platform init enables native or spapr XIVE, per-CPU setup maps TIMA and event queues, per-IRQ data caches ESB trigger/EOI pages, and KVM/native APIs allocate VPs, configure queues, sync sources/queues, and expose queue state.

State and persistence: Persistent state includes global enable/TIMA mapping, per-IRQ ESB data and saved/stale P flags, per-CPU queue indexes/toggles/counters, guest queue fields, and firmware-backed VP/IRQ allocations.

Dependencies and integration points: Depends on OPAL API, irq chips, atomic counters, MMIO mapping, SMP setup, and KVM. Stubbed out when `CONFIG_PPC_XIVE` is disabled.

Risks: EOI/trigger page handling is concurrency-sensitive. Saved/stale P bookkeeping must match queue state or interrupts can be lost or duplicated. KVM escalation interrupts may skip normal EOI.

Test signals: Native/spapr XIVE boot, IRQ affinity and hotplug, KVM guest interrupt tests, queue state save/restore, xmon dumps, and disabled-config compile coverage.

Source read size: 168 lines, 5147 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive.h -->
