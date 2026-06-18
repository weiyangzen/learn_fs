<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-regs.h

## Purpose
`solo6x10-regs.h` is the central register map and bitfield definition header for the SOLO6010/SOLO6110 PCI video/audio processor.

## Important APIs, Types, and Functions
The header defines MMIO offsets and field macros for system clock/reset, DMA and SDRAM, IRQ status/masks, P2M engines, video input/output, display windows, motion detection, capture, video encoder/decoder queues, GPIO, IIC, UART, timers, watchdog, and audio. It includes `solo6x10-offsets.h` and Linux bit operations.

## Control Flow
There is no executable control flow. Runtime code uses these macros through `solo_reg_read()` and `solo_reg_write()` from `solo6x10.h` to program hardware blocks.

## State and Persistence
The header does not own state, but every defined register corresponds to volatile device state. Some macros distinguish SOLO6110-only fields such as extended JPEG/MPEG size bits, H.264-related behavior, and timer LSB support.

## Dependencies and Integration Points
All SOLO subsystem files depend on this header for register names and bit packing. The definitions are the integration contract between V4L2 display/encoder, ALSA, I2C, GPIO, P2M DMA, motion, OSD, and the top-level PCI driver.

## Risks and Edge Cases
Bitfield macros mostly shift unchecked input values, so callers must validate ranges. Register comments include undocumented hardware behavior and typos inherited from datasheets, making empirical tests important. Changing a shared macro can affect unrelated subsystems because the header is global to the driver.

## Test Signals
Build coverage across all SOLO files, successful probe on 6010 and 6110 hardware, correct IRQ masks, functional P2M/I2C/GPIO/audio/video blocks, and regression tests around 6110-only fields are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-regs.h -->
