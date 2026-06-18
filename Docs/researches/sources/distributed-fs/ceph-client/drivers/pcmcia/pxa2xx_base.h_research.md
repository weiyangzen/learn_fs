# sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_base.h

Purpose: Declares the public PXA2xx PCMCIA glue functions shared between board-specific socket code and the PXA2xx base driver.

Important APIs and types: Declares `pxa2xx_drv_pcmcia_add_one()`, `pxa2xx_drv_pcmcia_ops()`, and `pxa2xx_configure_sockets()`.

Control flow: No direct logic. Board/platform glue calls these functions to install PXA timing callbacks, configure the PXA socket controller, and register one `soc_pcmcia_socket`.

State and persistence: No state is stored here. The prototypes operate on `struct soc_pcmcia_socket`, `struct pcmcia_low_level`, and `struct device`, with state maintained by `soc_common.c` and `pxa2xx_base.c`.

Dependencies and integration points: This header is coupled to `soc_common.h` definitions and the PXA platform driver. It is consumed by `pxa2xx_base.c` and board files such as `pxa2xx_sharpsl.c`.

Risks: Signature changes must be synchronized with all board-specific users. Since platform data low-level ops are mutated by `pxa2xx_drv_pcmcia_ops()`, callers must provide mutable ops storage.

Test signals: Compile/link coverage for PXA2xx PCMCIA and successful board driver probe using these exported functions.
