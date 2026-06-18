# sources/distributed-fs/ceph-client/drivers/reset/reset-a10sr.c

Purpose: reset provider for the Altera Arria10 MAX5 System Resource Chip external reset functions.

Important APIs/types/functions: `struct a10sr_reset`, `a10sr_reset_shift()`, `a10sr_reset_update()`, assert/deassert/status ops, and `a10sr_reset_probe()`.

Control flow: reset IDs from `altr,rst-mgr-a10sr.h` map to chip register bit offsets. Probe gets parent MFD data, reuses the parent regmap, initializes `reset_controller_dev`, and registers devm-managed. Assert writes active-low reset state by clearing the bit; deassert sets it.

State and persistence: hardware register bits persist; driver caches only the parent regmap pointer and controller metadata.

Dependencies and integration: depends on `MFD_ALTERA_A10SR`, regmap, platform bus, OF match, and reset framework.

Risks and test signals: `a10sr_reset_shift()` returns negative for invalid IDs, but callers rely on framework ID bounds and mapped dt-bindings. Status polarity is easy to misread. Test every defined reset ID, invalid ID handling, parent data availability, and MFD probe ordering.
