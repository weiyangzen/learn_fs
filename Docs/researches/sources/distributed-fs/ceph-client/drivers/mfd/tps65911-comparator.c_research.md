# sources/distributed-fs/ceph-client/drivers/mfd/tps65911-comparator.c

## Purpose
`tps65911-comparator.c` is a small platform child driver for the TPS65911 voltage comparators. It programs comparator thresholds from parent board data and exposes read-only sysfs files reporting the selected threshold for comparator 1 and comparator 2.

## Important APIs, Types, And Functions
The comparator table is `tps_comparators[]`, with `COMP1` using `TPS65911_VMBCH` and `COMP2` using `TPS65911_VMBCH2`. `COMP_VSEL_TABLE[]` maps register selector values to millivolt thresholds. `comp_threshold_set()` chooses the first table value at or above the requested threshold and writes selector bits. `comp_threshold_get()` reads the register and returns the table value. Sysfs show path is `comp_threshold_show()`. Probe/remove are `tps65911_comparator_probe()` and `tps65911_comparator_remove()`.

## Control Flow
Probe obtains the parent `struct tps65910` and parent platform data, writes COMP1 and COMP2 thresholds from `vmbch_threshold` and `vmbch2_threshold`, then creates `comp1_threshold` and `comp2_threshold` sysfs files. Remove deletes both files. The driver registers at `subsys_initcall()`.

## State, Persistence, And Dependencies
The driver keeps no private state. Persistent effects are threshold register writes through the parent regmap. It depends on parent platform data being present and populated, `dev_get_drvdata(pdev->dev.parent)`, regmap, sysfs device attributes, and `linux/mfd/tps65910.h`.

## Integration Points
It is intended as a child of the TPS65910/TPS65911 MFD parent, even though the parent child table in the inspected source does not list this cell directly. It relies on the parent regmap and threshold board data parsed or supplied by `tps65910.c`.

## Risks
Probe dereferences `pdata` without checking for NULL, so OF-only systems must ensure the parent has compatible board data if this child is instantiated. `comp_threshold_set()` does not bounds-check the table index before reading, relying on reaching `uV_max`; malformed tables could overrun. If creating the first sysfs file succeeds and the second fails, probe returns the second error without removing the first. The sysfs attributes are read-only; thresholds cannot be changed after probe.

## Test Signals
Test threshold selection around duplicate 2500 mV entries, maximum and over-maximum inputs, regmap read/write failures, missing parent platform data, sysfs content for both attributes, and cleanup after probe failure or remove.
