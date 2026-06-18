# sources/distributed-fs/ceph-client/arch/sh/include/asm/dmabrg.h



Source read size: 24 lines, 536 bytes.



Purpose: SH7760 DMABRG public IRQ API.

Important APIs/types/functions: DMABRG IRQ source constants and `dmabrg_request_irq()`/`dmabrg_free_irq()`.

Control flow: drivers register callbacks for USB/audio bridge events.

State and persistence: handler storage lives in dmabrg.c.

Dependencies and integration points: SH7760 USB/audio DMA users.

Risks and test signals: wrong source ID dispatches incorrect callback. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
