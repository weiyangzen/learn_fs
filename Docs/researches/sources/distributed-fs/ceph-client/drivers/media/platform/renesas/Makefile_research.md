# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/Makefile

Purpose: kbuild dispatcher for Renesas media platform drivers.

Important APIs/types/functions: unconditionally descends into `rcar-isp/`, `rcar-vin/`, `rzg2l-cru/`, `rzv2h-ivc/`, and `vsp1/`; conditionally builds single-object drivers for R-Car CSI-2, DRIF, CEU, FCP, FDP1, JPU, and SH VOU.

Control flow: kbuild uses `obj-y` for subdirectories and `obj-$(CONFIG_...)` for individual modules/objects based on Kconfig symbols.

State and persistence: build graph only.

Dependencies and integration: must stay aligned with `renesas/Kconfig` symbols and source filenames such as `rcar-csi2.o`, `rcar_drif.o`, `renesas-ceu.o`, `rcar-fcp.o`, `rcar_fdp1.o`, `rcar_jpu.o`, and `sh_vou.o`.

Risks: unconditional subdirectory descent requires child Makefiles to be safe for disabled configs. Filename/symbol drift causes missing objects or unused Kconfig options.

Test signals: build Renesas media drivers as modules and built-ins, allmodconfig link checks, and disabled-symbol builds to ensure unconditional subdirectories are harmless.
