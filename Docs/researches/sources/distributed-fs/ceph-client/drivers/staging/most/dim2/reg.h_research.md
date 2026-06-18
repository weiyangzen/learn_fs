# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/reg.h

## Purpose
Defines the DIM2/OS62420 MMIO register layout and bit-field constants used by the HAL.

## Important APIs, Types, And Functions
`struct dim2_regs` maps MediaLB, HBI, data transfer, and AHB control/status registers with reserved gaps. `DIM2_MASK()` builds low-bit masks. Enum constants define MLBC0 clock/lock/enable/fcnt fields, MIEN interrupt bits, MLBC1 error/NDA fields, ACTL/HCTL fields, CDT buffer/read-pointer fields, ADT control/status/address fields, and CAT channel table fields for type, enable, read/write, and channel label.

## Control Flow
No executable flow. `hal.c` uses the layout and constants for all MMIO and control table programming.

## State And Persistence
Describes volatile hardware state only.

## Dependencies And Integration Points
Depends on Linux integer types. Included by `hal.h` and `hal.c`.

## Risks And Test Signals
Register layout mismatches cause all HAL behavior to fail. Test signals are MMIO smoke tests on supported hardware, lock-state reads, channel table programming, interrupt mask/status behavior, and DMA transfer completion.
