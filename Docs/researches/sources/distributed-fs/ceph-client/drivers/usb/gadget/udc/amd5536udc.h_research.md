# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/amd5536udc.h

Purpose: shared hardware definitions and core data structures for the AMD5536/Synopsys USB 2.0 device controller implementation.

Important APIs, types, and functions: register offsets and bit masks cover global CSRs, device configuration/control/status/interrupt registers, endpoint registers, FIFO sizes, setup command words, and DMA descriptor status fields. `struct udc_regs`, `struct udc_ep_regs`, `struct udc_stp_dma`, and `struct udc_data_dma` model hardware layout. `struct udc_request`, `struct udc_ep`, and `struct udc` are the software request, endpoint, and device objects. It declares core functions such as `udc_irq`, `udc_probe`, `udc_remove`, `init_dma_pools`, `free_dma_pools`, and `udc_basic_init`. Module parameters `use_dma`, `use_dma_ppb`, `use_dma_ppb_du`, and `use_fullspeed` tune operation.

Control flow: this header is consumed by PCI/platform glue and core controller code. Register macros feed initialization, interrupt handling, endpoint enablement, DMA descriptor construction, and setup packet decoding. Data structures hold queues, DMA pools, endpoint registers, FIFO pointers, UDC state, extcon/PHY support, and gadget core linkage.

State and persistence: no executable state except static module-parameter variables when included into implementation units. Runtime state lives in `struct udc`, protected by `dev->lock`, and includes current configuration/interface/altsetting, DMA pools, connection flags, and endpoint queues.

Dependencies and integration points: depends on USB ch9, gadget core, extcon, PHY, DMA pool usage, and PCI/platform glue. It also connects to Synopsys core support selected through Kconfig.

Risks: packed/aligned structures must match hardware DMA/register layout exactly. Bitfield macros and constants are widely reused, so a wrong mask or offset corrupts hardware programming. Static module parameters in a header are unusual and require careful inclusion expectations. DMA alignment and 32-bit address constraints are highlighted by the PCI driver comments.

Test signals: compile all users, boot/probe hardware in DMA and PIO modes, enumerate at full/high speed, exercise endpoint interrupts and setup commands, run with `use_fullspeed`, validate DMA descriptor ownership transitions, and run sparse/endianness checks over register access.
