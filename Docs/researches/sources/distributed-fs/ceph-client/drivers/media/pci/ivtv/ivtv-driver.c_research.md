# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-driver.c

## Purpose
`ivtv-driver.c` is the main PCI driver. It handles module parameters, PCI device matching, card autodetection, EEPROM processing, core `struct ivtv` initialization, MMIO setup, GPIO and I2C bring-up, subdevice loading, IRQ and stream registration, first-open firmware initialization, and device removal.

## Important APIs, Types, and Functions
Important globals include `ivtv_first_minor`, `ivtv_ext_init`, `ivtv_debug`, optional `ivtv_fw_debug`, module parameter arrays, and `ivtv_pci_driver`. Core helpers include `ivtv_process_options()`, `ivtv_process_eeprom()`, `ivtv_init_struct1()`, `ivtv_init_struct2()`, `ivtv_setup_pci()`, `ivtv_load_and_init_modules()`, `ivtv_probe()`, `ivtv_init_on_first_open()`, and `ivtv_remove()`. Utility exports include IRQ mask helpers, output-mode helpers, EEPROM read, wait helpers, and first-open initialization.

## Control Flow
Module init validates parameters and registers a PCI driver for Conexant vendor/device IDs. Probe allocates `struct ivtv`, registers a V4L2 device, parses options, identifies a card by user parameter, Hauppauge EEPROM, or PCI subsystem IDs, initializes locks/workers/control handlers, configures PCI and MMIO windows, initializes GPIO and I2C, loads subdevices, chooses tuner/radio/std settings, registers IRQ and V4L2 streams, and schedules optional ivtv-alsa loading. Firmware is intentionally loaded on first open, where the driver retries firmware init, configures initial frequency/input/std, initializes decoder output on CX23415 cards, enables interrupts, and sets up controls. Remove stops streams, halts firmware, shuts down IRQ/DMA/worker resources, unregisters streams/subdevices, and frees VBI buffers and the V4L2 device.

## State and Persistence
Runtime state is per PCI function in `struct ivtv`. Persistent external state is limited to module parameters and card EEPROM reads; driver state itself is volatile. The driver caches selected card descriptors, standards, tuner settings, stream buffers, IRQ masks, firmware mailbox pointers, VBI/YUV state, and subdevice pointers. `IVTV_F_I_INITED` and `IVTV_F_I_FAILED` gate first-open initialization.

## Dependencies and Integration Points
The file integrates with PCI, V4L2 device/control frameworks, cx2341x firmware API, tveeprom, I2C, GPIO, irq handling, DMA/UDMA, stream registration, routing/ioctl helpers, ivtv-alsa extension loading, and optional ivtvfb/IR exported symbols.

## Risks and Edge Cases
Probe has many staged failure exits, so resource ownership must stay aligned with devm-managed MMIO, manually allocated workers, IRQs, I2C adapters, and controls. Card autodetection may default to PVR-150 for unknown hardware. PVR-500 radio correction depends on PCI slot heuristics. Firmware failures are deferred until first open, meaning device nodes may exist before hardware is usable. `ivtv_set_output_mode()` allows only the first decoder output mode until reset.

## Test Signals
Test clean module load/unload, parameter validation, cardtype ignore and force modes, Hauppauge EEPROM variants, unknown card fallback logs, PCI latency and MMIO failures, I2C/subdevice detection, IRQ registration, stream node creation, first-open firmware retry and failure flags, capture and decoder startup, ivtv-alsa callback loading, and remove while capture/decoding is active.
