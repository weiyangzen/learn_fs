# sources/distributed-fs/ceph-client/include/linux/mtd/nand-gpio.h

## Purpose

Declares platform data for GPIO-driven raw NAND control lines.

## Important APIs, Types, and Functions

The exported type is `struct gpiomtd_platform_data`, carrying GPIO numbers/line names and an embedded platform NAND data object.

Source-visible symbols include structs: `struct gpio_nand_platdata`, `struct mtd_partition *parts;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_NAND_GPIO_H`.

## Control Flow

A GPIO NAND driver consumes the platform data to map CLE/ALE/NCE/RDY and I/O resources, then delegates chip behavior through platform/raw NAND structures.

## State and Persistence Behavior

Only static board configuration is described; no persistent state exists.

## Dependencies and Integration Points

It depends on platform NAND/raw NAND declarations and board-specific GPIO numbering.

Direct includes observed in the source are: `#include <linux/mtd/rawnand.h>`.

## Risks and Edge Cases

Wrong GPIO polarity or line assignment can corrupt command/address cycles or ready/busy polling.

## Test Signals

Probe with valid/invalid GPIOs, command/control toggling traces, and ready/busy timeout behavior.

Source read signal: 15 lines, 330 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
