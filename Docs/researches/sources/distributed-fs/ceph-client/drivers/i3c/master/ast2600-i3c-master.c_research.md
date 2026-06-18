# sources/distributed-fs/ceph-client/drivers/i3c/master/ast2600-i3c-master.c

Purpose: ASPEED AST2600 platform wrapper for the shared DesignWare I3C master. It configures AST2600 global registers, SDA pull-up strength, instance ID, and an IBI PEC workaround.

Important APIs/types/functions: `struct ast2600_i3c` embeds `struct dw_i3c_master` and adds regmap, global index, and pull-up setting. `ast2600_i3c_pullup_to_reg()` validates supported pull-ups. `ast2600_i3c_init()` writes AST global REG0/REG1. `ast2600_i3c_set_dat_ibi()` modifies DW DAT entries for PEC. Probe parses `aspeed,global-regs` and `sda-pullup-ohms`, then calls `dw_i3c_common_probe()`.

Control flow: Probe obtains the syscon regmap and controller index, defaults pull-up to 2000 ohms when absent, validates it, installs platform ops, and delegates to DW common registration. During DW bus init the wrapper writes global setup. During DW IBI enable it may set `DEV_ADDR_TABLE_IBI_PEC`.

State and persistence: Wrapper state is global regmap/index and pull-up. Hardware global registers retain pull-up and instance ID until reset; DAT PEC bits persist per enabled IBI entry.

Dependencies/integration: MFD syscon, regmap, OF, platform devices, `dw-i3c-master.h`, and DW common probe/remove exports. Binds to `aspeed,ast2600-i3c`.

Risks: Only 2000, 750, and 545 ohm values are accepted. PEC workaround intentionally truncates one IBI payload byte for payload-capable devices. Missing `aspeed,global-regs` fails probe.

Test signals: DT parsing for syscon and pull-up values, global register writes, DW registration, IBI payload behavior with PEC workaround, and common remove.
