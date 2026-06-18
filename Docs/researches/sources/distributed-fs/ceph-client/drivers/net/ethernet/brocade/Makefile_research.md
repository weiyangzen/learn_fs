# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/Makefile

Purpose: top-level kbuild entry for QLogic/Brocade BR-series Ethernet drivers.

Important APIs/types/functions: contains a single object rule, `obj-$(CONFIG_BNA) += bna/`, which descends into the BNA driver directory when the driver symbol is enabled.

Control flow: during kernel build, kbuild evaluates `CONFIG_BNA`; if built-in or module, it visits `drivers/net/ethernet/brocade/bna/` and uses that subdirectory's Makefile to compose `bna.o`.

State and persistence behavior: no runtime state. Build output depends on the persistent kernel config and generated object/module files.

Dependencies and integration points: integrates with the parent Ethernet Makefile and the child `bna/Makefile`. It relies on Kconfig to define `CONFIG_BNA`.

Risks: a wrong object directory or symbol name would omit the driver even when configured. Because the file only delegates, most build-order risk is in the child Makefile.

Test signals: `make M=drivers/net/ethernet/brocade` or a full kernel build with `CONFIG_BNA=m/y` should enter the `bna` directory and produce the driver object/module.
