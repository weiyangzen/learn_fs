# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7785.c

Purpose: registers the SH7785 PFC MMIO block.

Important APIs, types, and functions: `plat_pinmux_setup()` calls `sh_pfc_register("pfc-sh7785", ...)`; resource 0 maps `0xffe70000-0xffe7008f`.

Control flow: `arch_initcall` registers the PFC resources during early platform initialization for later PFC driver binding.

State and persistence: local state is static resource metadata only.

Dependencies and integration points: integrates with the SH7785 PFC driver and setup code for SCIF, TMU, DMA, and external IRQ/IRL pin selection.

Risks: wrong resource address corrupts pin-function access. No fallback exists if the PFC driver is absent.

Test signals: `pfc-sh7785` probe success and working SCIF/TMU board pins are the main integration signals.
