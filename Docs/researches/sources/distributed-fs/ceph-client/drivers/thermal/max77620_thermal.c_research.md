# sources/distributed-fs/ceph-client/drivers/thermal/max77620_thermal.c

Purpose: Maxim MAX77620 PMIC junction temperature thermal driver. The PMIC exposes threshold status rather than a continuous die temperature, so the driver reports nominal 100 C, alarm1 120 C, or alarm2 140 C based on status bits and updates the thermal framework from alarm IRQs.

Important APIs/types/functions: `struct max77620_therm_info` stores the parent regmap, thermal zone, IRQs, and device pointer. `max77620_thermal_read_temp()` reads `MAX77620_REG_STATLBT` and maps `MAX77620_IRQ_TJALRM1_MASK`/`TJALRM2_MASK` to fixed millidegree temperatures. `max77620_thermal_irq()` logs warning/critical messages depending on which shared IRQ fired, then calls `thermal_zone_device_update()`. Probe obtains two IRQs, parent regmap, inherits parent OF node, registers thermal zone 0, and requests both threaded IRQs.

Control flow: thermal reads are pure regmap status reads. IRQs are asynchronous hints that status changed; the framework rereads via the zone callback. All allocations and registrations are devm-managed.

State/persistence: no mutable driver state beyond handles; hardware status and parent PMIC interrupt controller provide persistence. Dependencies/integration: MAX77620 MFD definitions and regmap, platform ID `max77620-thermal`, thermal OF, two shared threaded IRQs.

Risks: temperatures are coarse estimates, not measurements; missing either IRQ fails probe with `-EINVAL`; `device_set_of_node_from_dev()` ties thermal-zone configuration to parent node lifetime. Test signals include status-bit priority when both alarms are set, IRQ-triggered updates, parent regmap absence, missing IRQs, and OF thermal trip registration.
