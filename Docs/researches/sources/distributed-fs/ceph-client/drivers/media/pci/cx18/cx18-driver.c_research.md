# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-driver.c

## Purpose
This is the main PCI module implementation for cx18. It owns module parameters, PCI probe/remove, board autodetection, global device initialization, first-open firmware bootstrap, stream registration, and cleanup.

## Important APIs, Types, and Functions
Important entry points are PCI callbacks `cx18_probe()` and `cx18_remove()`, module init/exit `module_start()` and `module_cleanup()`, first-open initializer `cx18_init_on_first_open()`, option parsing `cx18_process_options()`, EEPROM handling `cx18_read_eeprom()` and `cx18_process_eeprom()`, PCI setup `cx18_setup_pci()`, and subdevice setup `cx18_init_subdevs()`. It exports `cx18_ext_init` for the ALSA extension and `cx18_msleep_timeout()`.

## Control Flow
Module init validates parameters and registers a PCI driver. Probe allocates `struct cx18`, registers V4L2 device state, selects a card by module option, Hauppauge EEPROM, PCI ID, or default fallback, initializes locks/queues/control handlers, enables PCI and maps the 64 MiB memory window, initializes power, DDR, SCB, GPIO, A/V decoder, I2C, IRQ, tuner, streams, and video devices, then schedules asynchronous `cx18-alsa` loading. First open loads CPU/APU firmware twice for a silicon workaround, resets APU audio, loads A/V decoder firmware, selects input, standard, and initial frequency. Remove stops capture, disables interrupts, cancels work, halts firmware, unregisters streams/I2C/IRQ, unmaps memory, frees VBI buffers and controls, and unregisters V4L2.

## State and Persistence
Runtime state is almost entirely in `struct cx18`: module-derived options, selected card, stream buffers, controls, workqueues, VBI state, MMIO pointers, IRQ masks, I2C adapters, subdev pointers, and capture counters. No state is persisted beyond module/device lifetime.

## Dependencies and Integration Points
It integrates PCI, DMA, V4L2, cx2341x controls, firmware, SCB, mailbox, I2C, GPIO, A/V decoder, stream registration, DVB, and optional ALSA. Board data from `cx18-cards.c` drives many later steps.

## Risks and Edge Cases
Probe has many partial-initialization exits, so cleanup order is critical. `cx18_instance` is incremented before allocation and is not decremented on probe failure. Firmware is delayed until first open, so probe can succeed while capture later fails. The double firmware load and APU reset sequence are hardware workarounds that should not be simplified without regression testing.

## Test Signals
Validate forced and autodetected card types, bad module parameters, missing firmware, repeated open/close, module unload while capturing, IRQ sharing, I2C adapter creation, stream device node registration, and ALSA extension loading.
