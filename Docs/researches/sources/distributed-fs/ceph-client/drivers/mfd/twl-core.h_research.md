# sources/distributed-fs/ceph-client/drivers/mfd/twl-core.h

## Purpose
`twl-core.h` is the local private interface between `twl-core.c` and TWL IRQ implementation files. It declares initialization and teardown functions for TWL6030 and TWL4030 IRQ support plus TWL4030 chip-specific IRQ table selection.

## Important APIs, Types, And Functions
The declarations are `twl6030_init_irq()`, `twl6030_exit_irq()`, `twl4030_init_irq()`, `twl4030_exit_irq()`, and `twl4030_init_chip_irq()`. The header has a conventional include guard and includes no other headers.

## Control Flow
There is no executable control flow in this header. `twl-core.c` includes it and calls the declared functions during probe and remove according to chip class and IRQ availability.

## State, Persistence, And Dependencies
The header owns no state. It depends on `struct device` being declared before prototypes are consumed by compiling C files through their included Linux headers.

## Integration Points
It keeps TWL IRQ implementation symbols private to the MFD directory rather than exposing them through public `include/linux/mfd/twl.h`. `twl4030-irq.c` implements the TWL4030 declarations; TWL6030 support is expected from a sibling file outside this work item.

## Risks
Because no forward declaration for `struct device` appears in this header, it relies on include order in users. Any new C file including only this header would need to include a device declaration first. The API is narrow and class-specific, so adding new TWL IRQ variants requires updating this private contract.

## Test Signals
Build coverage is the main signal: compile `twl-core.c`, `twl4030-irq.c`, and TWL6030 IRQ implementation together with warnings enabled, and verify prototypes match definitions.
