# sources/distributed-fs/ceph-client/drivers/clk/nxp/Makefile

Purpose: Builds NXP LPC clock drivers for LPC18xx/LPC43xx and LPC32xx families.

Important APIs, types, and functions: `CONFIG_ARCH_LPC18XX` selects `clk-lpc18xx-cgu.o`, `clk-lpc18xx-ccu.o`, and `clk-lpc18xx-creg.o`. `CONFIG_ARCH_LPC32XX` selects `clk-lpc32xx.o`.

Control flow: Kbuild links the correct clock provider set for the selected architecture. LPC18xx needs separate CGU, CCU, and CREG providers; LPC32xx is a single large provider plus a USB sub-provider inside one object.

State and persistence: No runtime state; object inclusion only.

Dependencies and integration points: Must align with the architecture Kconfig symbols and OF compatibles implemented by each source file.

Risks: No `COMPILE_TEST` conditions appear here, so broad build coverage depends on architecture config. Splitting LPC18xx across three objects means missing one object can leave DT clock providers unresolved.

Test signals: Build `ARCH_LPC18XX` and `ARCH_LPC32XX` configs and verify all selected objects link. Boot DTs should find matching providers for CGU, CCU, CREG, and LPC32xx USB clock nodes.
