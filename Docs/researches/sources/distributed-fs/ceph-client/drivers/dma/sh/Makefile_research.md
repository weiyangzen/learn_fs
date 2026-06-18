# sources/distributed-fs/ceph-client/drivers/dma/sh/Makefile

Purpose: kbuild rules for Renesas/SuperH DMAEngine helper and controller objects.

Important APIs/types/functions: builds `shdma-base.o` for `CONFIG_SH_DMAE_BASE`; assembles `shdma.o` from `shdmac.o` for `CONFIG_SH_DMAE`; builds `rcar-dmac.o`, `usb-dmac.o`, and `rz-dmac.o` for their respective symbols.

Control flow: Kconfig selections decide which objects enter the kernel or modules. The intermediate `shdma-y`/`shdma-objs` variables make the legacy SH DMA controller extensible if more objects are added.

State/persistence: no runtime state.

Dependencies/integration: depends on Kconfig symbol names in `sh/Kconfig` and parent DMA kbuild inclusion.

Risks: adding helper files for `shdma.o` requires updating `shdma-y`. Object names must stay aligned with implementation filenames in this directory.

Test signals: per-symbol build tests for `SH_DMAE_BASE`, `SH_DMAE`, `RCAR_DMAC`, `RENESAS_USB_DMAC`, and `RZ_DMAC`, including module builds where symbols are tristate.
