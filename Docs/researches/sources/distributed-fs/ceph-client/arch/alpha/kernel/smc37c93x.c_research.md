# sources/distributed-fs/ceph-client/arch/alpha/kernel/smc37c93x.c

## Purpose
`smc37c93x.c` initializes SMC FDC37C93x Ultra I/O controllers on Alpha systems. It probes standard Super I/O config ports, enables legacy serial, parallel, keyboard/mouse, and floppy functions, and leaves IDE disabled for boards such as PC164 that use a PCI IDE controller.

## Important APIs, Types, And Functions
- Logical device constants identify FDC, IDE1/2, PARP, serial ports, RTC, keyboard, and AUX I/O.
- Register constants model logical device selection, device ID/revision, power, activation, base address, interrupt, and DMA registers.
- `SMCConfigState()` enters config mode, retries device ID reads, and returns the base address when `VALID_DEVICE_ID` is found.
- `SMCRunState()` exits config mode.
- `SMCDetectUltraIO()` probes 0x3f0 and 0x370.
- `SMCEnableDevice()` selects a logical device, programs base address and primary interrupt, and activates it.
- `SMCEnableKYBD()` programs keyboard and mouse interrupt lines and activates the logical keyboard device.
- `SMCEnableFDC()` enables floppy burst mode, IRQ 6, DMA 2, and activates FDC.
- `SMCReportDeviceStatus()` is debug-only status output.
- `SMC93x_Init()` is the exported `__init` entry point.

## Control Flow
`SMC93x_Init()` disables local interrupts, probes for the controller, optionally reports debug state, enables SER1 at COM1/IRQ4, SER2 at COM2/IRQ3, parallel at 0x3bc/IRQ7, keyboard/mouse at IRQ1/12, and FDC at IRQ6/DMA2. It exits config mode, restores interrupts, logs success, and returns `1`. On no device found, it restores interrupts and returns `0`.

## State And Persistence
The Super I/O chip persists programmed logical device activation and resource registers until reset. The code has no long-lived kernel state beyond hardware side effects. All helpers are `__init`.

## Dependencies And Integration Points
The file uses ISA `inb/outb`, early delay, local interrupt save/restore, and is invoked by board PCI init paths such as `alphapc164_init_pci()` in `sys_cabriolet.c`. Its resource choices affect serial, parport, keyboard, mouse, and floppy drivers.

## Risks
- Probe retries are simple and assume the device ID value `2`; other compatible revisions may not be detected.
- Resource programming is fixed; conflicts with firmware-assigned resources or variant board wiring would be problematic.
- Config mode remains active until `SMCRunState()` after all enables; failures mid-sequence could leave the chip in config mode.
- No explicit error checking exists for individual register writes.

## Test Signals
- Boot log `SMC FDC37C93X Ultra I/O Controller found @ ...`.
- Functional COM1/COM2, parallel port, keyboard/mouse, and floppy after boot.
- PC164/LX164 boards continue to use PCI IDE rather than Super I/O IDE.
- Absence of the controller returns 0 without disrupting boot.
