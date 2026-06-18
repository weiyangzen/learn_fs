# sources/distributed-fs/ceph-client/drivers/soc/ti/smartreflex.c

## Purpose
This file implements OMAP SmartReflex voltage-control hardware support. It registers SmartReflex instances, exposes configuration APIs to a class driver, handles interrupts, controls automatic voltage compensation, and provides debugfs controls/telemetry.

## Important APIs, Types, And Functions
Exported APIs include `sr_configure_errgen`, `sr_disable_errgen`, `sr_configure_minmax`, `sr_enable`, `sr_disable`, `sr_register_class`, `omap_sr_enable`, `omap_sr_disable`, and `omap_sr_disable_reset_volt`. Important helpers include `_sr_lookup`, `sr_interrupt`, `sr_set_clk_length`, `sr_late_init`, `sr_v1_disable`, `sr_v2_disable`, `sr_retrieve_nvalue_row`, and debugfs autocomp handlers.

## Control Flow
`omap_sr_probe` allocates an `omap_sr`, maps registers, gets optional IRQ and fck clock, copies platform data such as voltage domain, n-value table, sensor mods, limits, and IP type, adds the instance to `sr_list`, performs late init if a class is registered, and creates debugfs files. `sr_register_class` records class callbacks and late-initializes all existing instances. Class code calls configure/enable/disable APIs to program SRCONFIG, ERRCONFIG/IRQ registers, AVGWEIGHT, and NVALUERECIPROCAL. Global OMAP enable/disable APIs look up by voltage domain and delegate to class callbacks when autocomp is active.

## State And Persistence
Global state includes `sr_list`, singleton `sr_class`, and debugfs root. Per-instance state stores register base, clock, IRQ, voltage-domain pointer, n-value data, limits, sensor bits, `enabled`, and `autocomp_active`. Hardware state persists in SmartReflex registers and voltage processor interactions.

## Dependencies And Integration Points
It depends on platform data from OMAP voltage code, `linux/power/smartreflex.h`, voltage-domain APIs, clocks, runtime PM, debugfs, and optional IRQ lines. It integrates with SmartReflex class drivers that supply configure/enable/disable/notify callbacks.

## Risks And Test Signals
Risks include class-driver singleton ordering, platform-data absence, IP-version-specific status bit clearing mistakes, timeout on disable acknowledge, invalid fck rates, and debugfs-modifiable voltage n-values. Test signals include probe logs, debugfs `smartreflex/*/autocomp`, IRQ notification callbacks, successful enable/disable across OPP voltages, and timeout-free v1/v2 disable paths.
