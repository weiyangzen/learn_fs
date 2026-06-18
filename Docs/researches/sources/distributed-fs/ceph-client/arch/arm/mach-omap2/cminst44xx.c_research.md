# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cminst44xx.c

Purpose: Implements partitioned CM instance access and OMAP4-style clockdomain/module operations for OMAP4, OMAP5, DRA7xx, and AM43xx-style CM layouts.

Important APIs/types/functions: Maintains `_cm_bases[]`, initializes it from PRM/CM1/CM2/PRCM_MPU bases, implements partitioned register read/write/RMW helpers, IDLEST polling, CLKTRCTRL writes, module enable/disable, static dependency add/delete/read/clear, clockdomain sleep/wakeup/allow/deny/clock enable/disable, context save/restore, and `omap4_cm_init()`. Exports `omap4_clkdm_operations` and `am43xx_clkdm_operations`.

Control flow: `omap4_cm_init()` populates `_cm_bases` and registers `omap4xxx_cm_ll_data`. Common CM dispatch uses module operations and xlate. Generic clockdomain dispatch uses operation tables to program CLKSTCTRL or STATICDEP based on `prcm_partition`, `cm_inst`, and `clkdm_offs`.

State and persistence: `_cm_bases[]` stores physical/virtual bases per PRCM partition. Each clockdomain stores saved CLKSTCTRL mode in `clkdm->context`. Hardware CM registers hold active state.

Dependencies: Includes CM1/CM2 OMAP44xx headers, `cm44xx.h`, OMAP34xx regbit mode constants, PRCM/PRM partition headers, and generic clockdomain/CM definitions.

Integration points: Backend for OMAP44xx, OMAP54xx, DRA7xx, and AM43xx clockdomain data. It also services common module enable/disable operations for hwmod on OMAP4-style SoCs.

Risks: Invalid partition or unmapped base triggers BUG_ON. AM43xx uses a reduced operation table without dependency/context callbacks. `omap4_clkdm_save_context()` masks with MODULEMODE/CLKTRCTRL low bits; hardware encoding compatibility is assumed. Static dependency clearing only iterates `wkdep_srcs` for both wake and sleep clear callbacks.

Test signals: OMAP4/5/DRA7/AM43 boot should initialize partition bases before any CM access. Runtime PM should verify module ready/idle timeouts, static dependency bit changes, and suspend/resume context restore.
