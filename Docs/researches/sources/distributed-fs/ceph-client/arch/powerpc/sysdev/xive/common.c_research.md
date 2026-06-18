# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/common.c

## Purpose
`common.c` is the generic PowerPC XIVE interrupt-controller core. It connects Linux `irq_chip`, `irq_domain`, SMP IPI, CPU hotplug, xmon, and debugfs behavior to a backend-specific `struct xive_ops` implementation supplied by native OPAL or sPAPR. It owns interrupt queue scanning, source masking and EOI sequencing, CPU target selection, per-CPU queue setup, and global XIVE initialization.

## Important APIs, Types, And Functions
Global state includes `__xive_enabled`, `xive_tima`, `xive_tima_offset`, `xive_ops`, `xive_irq_domain`, `xive_irq_priority`, and per-CPU `struct xive_cpu *`. The main callbacks exposed to generic IRQ code are in `xive_irq_chip`: `xive_irq_startup`, `xive_irq_shutdown`, `xive_irq_eoi`, `xive_irq_mask`, `xive_irq_unmask`, `xive_irq_set_affinity`, `xive_irq_set_type`, `xive_irq_retrigger`, `xive_irq_set_vcpu_affinity`, and `xive_get_irqchip_state`. `xive_core_init` is the central backend entry point, and `xive_queue_page_alloc`, `xive_cleanup_irq_data`, `is_xive_irq`, SMP lifecycle helpers, teardown, shutdown, and debug init connect this core to the rest of PowerPC.

## Control Flow
Initialization records backend ops and TIMA mapping, installs `ppc_md.get_irq`, creates the IRQ domain, allocates the boot CPU queue, and enables CPU interrupt flow by setting CPPR to `0xff`. When an interrupt arrives, `xive_get_irq` asks the backend to acknowledge pending priorities, then `xive_scan_interrupts` consumes the highest-priority valid queue entry and updates CPPR. Startup chooses a target CPU, programs the backend with hardware target, priority, and Linux IRQ number, then unmasks the ESB. EOI updates source state, handles StoreEOI or legacy PQ/LSI paths, clears saved queue occupancy, and peeks for more queued work to trigger replay. Affinity changes pick a new target and defer old queue count cleanup until the old queue drains. KVM pass-through uses `xive_irq_set_vcpu_affinity` to move sources between host and guest while preserving pending P/Q state.

## State And Persistence
All state is runtime kernel state. Per-CPU `xive_cpu` records queue pages, pending priority bits, cached CPPR, chip id, and IPI metadata. Per-interrupt `xive_irq_data` records MMIO mappings, ESB flags, target CPU, saved/stale P state, and hardware IRQ id. Queue accounting uses `count` and `pending_count` atomics to avoid freeing capacity before stale queue entries are observed. Command-line settings persist only for the booted kernel: `xive=off` and `xive.store-eoi=off`.

## Dependencies And Integration Points
This file depends on Linux IRQ domains, generic IRQ descriptors, SMP, CPU hotplug, debugfs, xmon, Open Firmware device nodes, PowerPC TIMA and XIVE register definitions, and backend `xive_ops`. It integrates with KVM through forwarded IRQ handling, with xmon through dump helpers, with `arch_debugfs_dir` for diagnostics, and with backend native/sPAPR files for hardware programming.

## Risks
The riskiest paths are P/Q state transitions around mask, EOI, retrigger, shutdown, and KVM pass-through because losing `saved_p` or `stale_p` can drop or duplicate interrupts. Queue target accounting intentionally delays decrements, so changes can cause queue exhaustion or premature reuse. CPU hotplug flushes stale queue entries with descriptor locks and must not mishandle IPIs or non-XIVE IRQs. `xive_get_irq` drops `XIVE_BAD_IRQ` and warns on missing descriptors, which indicates shutdown synchronization failures.

## Test Signals
Coverage is mostly platform and boot-test driven: successful boot on XIVE native and pseries guests, interrupt delivery under load, CPU hotplug, affinity changes, MSI and LSI behavior, KVM device pass-through, IPI storms, and debugfs/xmon dumps. Build coverage should include `CONFIG_SMP`, `CONFIG_HOTPLUG_CPU`, `CONFIG_XMON`, `CONFIG_DEBUG_FS`, and irqdomain hierarchy variants.
