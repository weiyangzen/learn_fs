# sources/distributed-fs/ceph-client/arch/sh/cchips/Kconfig



Source read size: 46 lines, 1041 bytes.



Purpose: Kconfig menu for SuperH companion chips, currently the Hitachi HD6446x/HD64461 family and its IRQ/PCMCIA options.

Important APIs/types/functions: symbols `HD6446X_SERIES`, `HD64461`, `HD64461_IRQ`, and `HD64461_ENABLER`.

Control flow: enabling a board that selects HD6446x exposes the HD64461 choice; users can configure the parent IRQ number and optional PCMCIA enabler.

State and persistence: compile-time configuration only; selected symbols control which driver code and constants enter the kernel.

Dependencies and integration points: feeds `hd6446x/Makefile`, `hd64461.c`, IRQ descriptor setup, and PCMCIA board behavior.

Risks and test signals: wrong IRQ configuration prevents child interrupt demux; enabling PCMCIA on unsupported wiring can clear wrong status. Test Kconfig dependencies and boot with configured parent IRQ.
