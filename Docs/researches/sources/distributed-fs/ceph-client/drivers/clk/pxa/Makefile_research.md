# sources/distributed-fs/ceph-client/drivers/clk/pxa/Makefile

Purpose: Builds Marvell PXA clock support objects.

Important APIs, types, and functions: Always builds `clk-pxa.o`. Adds `clk-pxa25x.o` for `CONFIG_PXA25x`, `clk-pxa27x.o` for `CONFIG_PXA27x`, and `clk-pxa3xx.o` for `CONFIG_PXA3xx`.

Control flow: Kbuild links the common CKEN/DT/frequency-change helpers plus the selected SoC-specific topology file.

State and persistence: No runtime state; controls object inclusion.

Dependencies and integration points: Common `clk-pxa.o` is required by all PXA SoC files. The listed config symbols must match architecture support.

Risks: `clk-pxa3xx.o` is referenced but outside this work item; build coverage should ensure the common interfaces remain compatible across all PXA variants.

Test signals: Build PXA25x, PXA27x, and PXA3xx configs. Link errors around `clk_pxa_cken_init()` or `pxa2xx_*` helpers indicate Makefile/interface drift.
