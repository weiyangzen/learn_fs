# sources/distributed-fs/ceph-client/drivers/iommu/irq_remapping.c

## Purpose
`irq_remapping.c` is x86 interrupt-remapping orchestration code. It parses boot parameters, selects an Intel, AMD, or Hyper-V IRQ remapping backend, enables/disables remapping, exposes capability checks, and adjusts crash/boot IRQ restoration behavior when interrupt remapping is active.

## Important APIs, Types, and Functions
Global exported state includes `irq_remapping_enabled`, `irq_remap_broken`, `disable_sourceid_checking`, `no_x2apic_optout`, `disable_irq_post`, and `enable_posted_msi`. The backend is `static struct irq_remap_ops *remap_ops`, defined by the internal header.

Important functions are `setup_nointremap()`, `setup_irqremap()`, `irq_remapping_prepare()`, `irq_remapping_enable()`, `irq_remapping_disable()`, `irq_remapping_reenable()`, `irq_remap_enable_fault_handling()`, `irq_remapping_cap()`, `set_irq_remapping_broken()`, and `panic_if_irq_remap()`.

## Control Flow and State
Early parameters `nointremap` and `intremap=` update static policy flags before normal init. `intremap=` supports enabling/disabling remapping, disabling source-ID checks, forcing x2APIC optout behavior, disabling posted interrupts, and enabling posted MSI when configured. During preparation, the code skips work if remapping is disabled, then tries Intel, AMD, and Hyper-V `prepare()` methods in order based on Kconfig. The selected backend remains in `remap_ops`.

Enable calls the selected backend `enable()` and, if `irq_remapping_enabled` becomes true, replaces `x86_apic_ops.restore` with a virtual-wire-A-oriented restore path for crash dump simplicity. Fault handling installs a CPU hotplug online callback and invokes backend faulting setup on the current CPU. State is entirely boot/runtime kernel memory.

## Dependencies and Integration Points
The file integrates with x86 APIC setup, early boot parameters, backend IOMMU drivers, CPU hotplug, HPET/APIC headers, MSI and irqdomain infrastructure, and exported capability checks consumed by other IRQ/MSI code.

## Risks and Test Signals
Risks include backend selection order surprises when multiple IOMMU drivers are present, boot parameter parsing with comma-separated options, global posted-interrupt disablement hiding backend capabilities, and crash-kernel restore behavior. Test signals include booting with `intremap=on/off/nosid/nopost/posted_msi`, Intel/AMD/Hyper-V remapping paths, CPU online fault-handler setup, capability queries with and without `disable_irq_post`, and panic paths that must fire only when remapping is enabled.
