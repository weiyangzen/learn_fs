# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/Makefile

Purpose: Top-level build glue for Marvell OcteonTX2 networking drivers. It maps Kconfig symbols to subdirectories.

Important APIs/types/functions: `obj-$(CONFIG_OCTEONTX2_MBOX) += af/`, `obj-$(CONFIG_OCTEONTX2_AF) += af/`, and `obj-$(CONFIG_OCTEONTX2_PF) += nic/` are the functional entries. Both mailbox-only and AF builds descend into `af/`, while PF builds descend into `nic/`.

Control flow and integration: Kbuild evaluates the selected symbols and recursively builds the AF or NIC subdirectories. The duplicated `af/` dependency is intentional because mailbox objects live under the AF directory and may be needed independently of full AF support.

State and persistence: No runtime state. Build configuration determines which object directories become built-in or modules.

Dependencies: Depends on the Kconfig symbols from the sibling `Kconfig` and on subdirectory Makefiles under `af/` and `nic/`.

Risks: Because `af/` is included for two symbols, the lower-level Makefile must keep object lists separated by config to avoid duplicate or missing objects. Adding future subdirectories without matching Kconfig dependencies can break modular builds.

Test signals: `make M=...` or full kernel builds with mailbox-only, AF, and PF combinations should verify correct object inclusion and no duplicate symbol linkage.
