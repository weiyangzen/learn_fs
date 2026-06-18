# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/Kconfig

Purpose: Kconfig menu entries for the Freescale MPC5200 BestComm communication coprocessor support and its optional task families.

Important symbols: `PPC_BESTCOMM` is a tristate gated by `PPC_MPC52xx`, selects `PPC_LIB_RHEAP`, and represents the core BestComm engine/SRAM allocator. `PPC_BESTCOMM_ATA`, `PPC_BESTCOMM_FEC`, and `PPC_BESTCOMM_GEN_BD` are tristate task-library symbols that depend on the core.

Control flow: This file does not execute code; it controls which objects the sibling Makefile can build. The core help text notes ATA may use BestComm optionally, while FEC requires it for DMA operations. The task symbols intentionally have no prompts, making them selected/enabled by dependent drivers or board configuration rather than directly user-facing.

State and persistence: Configuration choices are persisted in the kernel `.config` and determine whether the BestComm support is built in, modular, or omitted.

Dependencies/integration: Integrated with PowerPC MPC52xx platform support, reusable heap allocator support, and downstream ATA/FEC/PSC users that consume exported BestComm task APIs.

Risks: Hidden task symbols can be missed if dependent drivers do not select them correctly. Building task modules without the core would be invalid, guarded by the dependencies. Platform specificity means accidental enablement outside MPC52xx is blocked.

Test signals: Kconfig dependency checks for MPC52xx-only builds, `make olddefconfig` preservation, module/built-in combinations for core and task libraries, and link tests confirming dependent users pull in the proper task symbol.
