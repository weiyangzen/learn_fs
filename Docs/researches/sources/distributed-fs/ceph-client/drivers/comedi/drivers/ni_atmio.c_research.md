# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_atmio.c

## Purpose
`ni_atmio.c` is the ISA/ISA-PnP front end for NI AT-MIO E-series boards. It defines board capability tables and attachment/probing logic, then includes and delegates most hardware operation to the shared `ni_mio_common.c` E-series implementation.

## Important APIs, Types, And Functions
The file defines `range_ni_E_ao_ext`, `ni_boards[]` entries of `struct ni_board_struct`, and the ISA IRQ-to-STC interrupt pin map `ni_irqpin[]`. It includes `"ni_stc.h"` and then `"ni_mio_common.c"`, making shared NI MIO functions and types part of this translation unit. ISA-PnP support uses `device_ids[]` and `ni_isapnp_find_board()`. `ni_atmio_probe()` reads EEPROM address 511 through `ni_read_eeprom()` to match `device_id`. `ni_atmio_attach()` performs private allocation, optional PnP discovery, I/O region request, board probe, IRQ request, and `ni_E_init()`. `ni_atmio_detach()` tears down shared MIO and PnP resources.

## Control Flow
When configured without an I/O base, attach scans known ISA-PnP IDs, activates the first valid device, extracts I/O base and IRQ, and binds the Comedi hardware device pointer to the PnP device. Otherwise it uses explicit config options. After requesting a 0x20-byte I/O region, the driver probes EEPROM device ID to choose a board descriptor. If an IRQ is configured, it validates the IRQ against `ni_irqpin[]`, requests it with `ni_E_interrupt`, and stores it. Shared NI E-series initialization then builds the actual AI/AO/DIO/counter/calibration subdevices according to board capabilities.

## State And Persistence
This file contributes static board metadata and no private state of its own beyond what `ni_alloc_private()` and `ni_mio_common.c` allocate. PnP attachment state is stored in `dev->hw_dev`; detach converts it back to `struct pnp_dev` and detaches it after common cleanup.

## Dependencies And Integration Points
Dependencies include Linux ISA-PnP, Comedi legacy attachment, optional 8255 support, `ni_stc.h`, and the included `ni_mio_common.c`. It is tightly coupled to shared NI MIO symbols such as `ni_alloc_private()`, `ni_read_eeprom()`, `ni_E_interrupt()`, `ni_E_init()`, and `mio_common_detach()`.

## Risks
Including a `.c` file is intentional in this driver family but creates tight compile-time coupling and can hide symbol ownership. Several board ISA-PnP IDs are unknown and cannot be autodetected. EEPROM probe failures produce user-facing errors but no fallback board selection. IRQ validation depends on the static `ni_irqpin[]` map. Calibration quality is explicitly poor at boot unless user-space calibration is applied.

## Test Signals
Tests should exercise explicit and auto PnP attach paths, PnP activation failure cleanup, I/O region bounds, EEPROM device ID matching and unknown-device errors, IRQ validation for accepted/rejected ISA IRQs, `ni_E_init()` invocation with correct IRQ pin, shared detach plus PnP detach, and board table correctness for AI/AO channels, FIFO depths, gain tables, caldac types, 8255 presence, and speed limits.
