# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_irqtrans.c

Purpose: translates Open Firmware interrupt numbers into Linux IRQs for SPARC64 PCI, SBUS, central, and sun4v virtual-device interrupt controllers. It attaches per-node `of_irq_controller` builders during early device-tree setup.

Important APIs/functions: main entry is `irq_trans_init()`. PCI builders include `psycho_irq_build()`, `sabre_irq_build()`, `schizo_irq_build()`, `pci_sun4v_irq_build()`, and `fire_irq_build()` with init functions for PSYCHO, Sabre, Schizo, Tomatillo, sun4v PCI, and Fire. SBUS uses `sbus_of_build_irq()`. Central FHC devices use `central_build_irq()`. Virtual devices use `sun4v_vdev_irq_build()`. DMA ordering prehandlers are `sabre_wsync_handler()` and `tomatillo_wsync_handler()`.

Control flow: `irq_trans_init()` matches a node by PCI model/compatible string, SBUS/SBI name, central/FHC placement, or virtual-device/NIU name, then allocates an IRQ translation object with `prom_early_alloc()`. Each builder masks or transforms the firmware INO/devino, computes controller-specific IMAP and ICLR register addresses, applies INO/IGN fixups where hardware requires them, and calls `build_irq()` or `sun4v_build_irq()`. Sabre and Tomatillo may install prehandlers that drain posted DMA writes before invoking device handlers.

State and persistence: per-device-node state is `dp->irq_trans` plus controller data such as base registers, sync registers, port IDs, chip version, and bus ranges. State exists for runtime IRQ construction and is not persistent.

Dependencies and integration points: depends on OF properties (`reg`, `model`, `compatible`, `bus-range`, `portid`, `version#`), UPA and physical-bypass ASI accesses, SPARC IRQ core (`build_irq`, `irq_install_pre_handler`, `sun4v_build_irq`), PCI/SBUS config layouts, and early PROM allocation.

Risks: register-offset tables are hardware ABI. Wrong INO fixups can route interrupts to the wrong target. Sabre/Tomatillo DMA synchronization is required for correctness behind certain bridges and can hang or log if sync never completes. Bad SYSIO INOs halt the machine. Model matching must include legacy compatible names.

Test signals: boot IRQ enumeration on PSYCHO, Sabre, Schizo, Tomatillo, Fire, SBUS/SYSIO, central, and sun4v virtual-device systems; functional PCI/SBUS device interrupts; DMA completion correctness behind bridges; and logs-free boot with valid `reg`/`model` data.
