# sources/distributed-fs/ceph-client/drivers/bus/vexpress-config.c

## Purpose
`vexpress-config.c` exposes ARM Versatile Express SYS_CFG functions as regmaps for devices below the vexpress config bus. It builds SYS_CFGCTRL command templates from devicetree topology properties and serializes register-like reads/writes through the board's configuration controller.

## Important APIs, Types, And Functions
`struct vexpress_syscfg` owns the SYS_CFG MMIO base and list of active function regmaps. `struct vexpress_syscfg_func` stores command templates and its regmap. `devm_regmap_init_vexpress_config()` is the exported consumer API. `vexpress_syscfg_exec()` performs one command, `vexpress_syscfg_regmap_init()` parses `arm,vexpress-sysreg,func`, and `vexpress_syscfg_probe()` maps the controller, determines the master site, validates optional HBI data, and populates config-bus children.

## Control Flow
Consumers call `devm_regmap_init_vexpress_config()` from a child device. The bridge init path resolves site/position/dcc inherited from devicetree, handles `VEXPRESS_SITE_MASTER`, parses pairs of function/device numbers, creates one SYS_CFGCTRL template per index, and initializes a regmap with custom read/write callbacks. Reads and writes acquire the shared mutex through regmap config, write data and command registers, then poll SYS_CFGSTAT until COMPLETE, ERR, timeout, or signal interruption.

## State And Persistence
The current master site is global. Per-consumer state persists in `vexpress_syscfg_func` until the devres cleanup calls `vexpress_syscfg_regmap_exit()`. Hardware state is transient command execution; persistent values live in the platform configuration registers behind SYS_CFG.

## Dependencies And Integration Points
The driver depends on platform MMIO resources, OF properties `arm,vexpress,site`, `arm,vexpress,position`, `arm,vexpress,dcc`, `arm,vexpress-sysreg,func`, and `arm,vexpress,config-bridge`, plus Linux regmap. It integrates with other vexpress drivers that need syscfg-backed regmaps.

## Risks And Edge Cases
The shared regmap config's `max_register` is mutated during each regmap init, which is safe only because init is serialized by probe/devres assumptions rather than per-instance config allocation. `vexpress_syscfg_exec()` can sleep unless interrupts are disabled, then falls back to `udelay`; callers in atomic contexts still risk long busy waits. The energy function compatibility quirk rewrites one legacy function into two templates. `vexpress_syscfg_regmap_exit()` deletes `&syscfg->funcs` rather than `&func->list`, which is suspicious and worth review.

## Test Signals
Exercise regmap reads/writes for multiple child functions, signal interruption during a long command, SYS_CFGSTAT error and timeout paths, HBI mismatch warnings, legacy `arm,vexpress-energy` nodes, and multiple children registering/releasing regmaps.
