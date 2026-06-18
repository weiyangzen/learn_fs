# sources/distributed-fs/ceph-client/include/linux/mtd/hyperbus.h

## Purpose

Provides the HyperBus controller/device abstraction used to expose HyperFlash or HyperRAM through MTD/map-style access.

## Important APIs, Types, and Functions

Key types are `enum hyperbus_memtype`, `struct hyperbus_device`, `struct hyperbus_ops`, and `struct hyperbus_ctlr`; exports are `hyperbus_register_device()` and `hyperbus_unregister_device()`.

Source-visible symbols include structs: `struct hyperbus_device`, `struct map_info map;`, `struct device_node *np;`, `struct mtd_info *mtd;`, `struct hyperbus_ctlr *ctlr;`, `struct hyperbus_ops`, `struct hyperbus_ctlr`, `struct device *dev;`; enums: `enum hyperbus_memtype`, `enum hyperbus_memtype memtype;`; typedefs: none visible in this header; prototypes: `int hyperbus_register_device(struct hyperbus_device *hbdev);`, `void hyperbus_unregister_device(struct hyperbus_device *hbdev);`; representative macros: `__LINUX_MTD_HYPERBUS_H__`, `HYPERBUS_RW_WRITE`, `HYPERBUS_RW_READ`, `HYPERBUS_AS_MEM`, `HYPERBUS_AS_REG`, `HYPERBUS_BT_WRAPPED`, `HYPERBUS_BT_LINEAR`.

## Control Flow

A controller supplies 16-bit register-space operations, copy operations, and optional calibration. Registration probes the HyperBus slave from its device node and controller ops, then creates an MTD device for flash-backed memory.

## State and Persistence Behavior

The device keeps its `map_info`, device tree node, resulting `mtd_info`, controller pointer, memory type, and private controller data. The controller tracks whether calibration has completed.

## Dependencies and Integration Points

It builds on `map.h`, device tree nodes, and MTD map probing. HyperFlash users depend on correct command/address-space bit construction.

Direct includes observed in the source are: `#include <linux/mtd/map.h>`.

## Risks and Edge Cases

Calibration state, burst type/address-space selection, and 16-bit transaction width are hardware-sensitive. Misclassification between HyperFlash and HyperRAM changes whether MTD registration is valid.

## Test Signals

Exercise controller ops against known ID/CFI space reads, registration failure cleanup, calibration-once behavior, and unregister paths.

Source read signal: 95 lines, 2893 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
