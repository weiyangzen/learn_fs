# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_init.c

Purpose: initializes and uninitializes the CSS input system for ISP2400 and ISP2401 variants.

Important functions: private `ia_css_isys_2400_init`, private `ia_css_isys_2401_init`, public `ia_css_isys_init`, and `ia_css_isys_uninit`.

Control flow: ISP2400 path resets input-system configuration, configures three CSI xmem channels with hard-coded memory/acquisition region sizes and targets, then commits. ISP2401 path initializes CSI RX LUT, IBUF, DMA, and stream2mmio resource managers, sets DMA0 max burst size to non-burst transactions, and enables ISYS IRQ status blocks. Public init selects by `IS_ISP2401`; uninit tears down ISP2401 resource managers.

State/persistence: hardware input-system configuration and resource-manager globals persist after init until uninit or reset.

Dependencies/integration: `input_system.h`, ISYS public APIs, `isys_dma_public.h`, and `isys_irq.h`.

Risks: ISP2400 configuration is hard-coded and must match hardware topology. ISP2401 init has no rollback if a later step fails, though it currently returns no-error after side effects.

Test signals: ISP2400 configuration failure propagation, ISP2401 resource managers reset, IRQ status enable effects, and repeated init/uninit cycles.
