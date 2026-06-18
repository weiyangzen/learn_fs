# sources/distributed-fs/ceph-client/drivers/input/touchscreen/htcpen.c

## Purpose
`htcpen.c` is an ISA I/O port touchscreen driver for the HTC Shift embedded controller. It is DMI-gated to HTC Shift systems, reads coordinates from fixed EC ports on IRQ 3, and reports a simple absolute touchscreen input device.

## Important APIs, types, and functions
- Module parameters `invert_x` and `invert_y` optionally flip axes.
- `htcpen_interrupt()` reads touch, X, Y, and low-bit registers through indexed I/O ports, reports `BTN_TOUCH`, `ABS_X`, and `ABS_Y`, and clears the IRQ.
- `htcpen_open()`/`htcpen_close()` send EC enable/disable commands and synchronize IRQ on close.
- `htcpen_isa_probe()` claims I/O port regions, allocates input, requests IRQ 3, clears pending IRQ state, registers input, and stores drvdata.
- `htcpen_isa_remove()` unregisters input, frees IRQ, and releases I/O regions.
- `htcpen_isa_init()` checks a DMI table before registering the ISA driver.

## Control flow
Module init refuses to load unless DMI matches the HTC Shift. ISA probe reserves ports `0x068`, `0x06c`, and `0x250-0x251`, creates an input device with 0..2040 axes, and requests the fixed IRQ. The input device open/close hooks enable or disable the EC. Each IRQ reads the current sample, ignores sentinel edge X values, reports contact/position or release, syncs, and clears the IRQ status port.

## State and persistence
Persistent driver state is limited to the input device pointer stored as ISA drvdata and module parameters. The EC enable state changes while the input device is open or during PM suspend/resume.

## Dependencies and integration points
This driver depends on x86-style port I/O, the ISA bus helper, DMI matching, fixed hardware resources, and the input subsystem.

## Risks
- Fixed ports and IRQ are safe only because of DMI gating; widening matching risks conflicts with unrelated hardware.
- I/O port access and coordinate bit assembly are hardware-specific and have no protocol validation.
- Resume unconditionally enables the device even if userspace had not opened it before suspend.
- Module parameters can invert axes but no dynamic calibration is provided.

## Test signals
- Confirm the DMI gate prevents loading on non-HTC Shift systems.
- On hardware, test port reservation conflicts, input open/close, IRQ clear behavior, axis inversion parameters, and suspend/resume enable state.
