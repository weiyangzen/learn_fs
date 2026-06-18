# sources/distributed-fs/ceph-client/drivers/parisc/lasi.c

## Purpose
This file is the driver for the LASI GSC bus adapter ASIC. It initializes the LASI interrupt controller, maps child devices to local interrupt lines, registers chassis LED support for LASI-based machines, and provides a power-off callback using the LASI power control register.

## Important APIs, Types, And Functions
Key functions are `lasi_choose_irq()`, `lasi_init_irq()`, optional `lasi_led_init()`, `lasi_power_off()`, `lasi_init_chip()`, and `lasi_init()`. It uses `struct gsc_asic` plus GSC helper APIs from `gsc.c`.

## Control Flow
At `arch_initcall`, the PA-RISC driver matches LASI bus adapters. Probe allocates a `gsc_asic`, records HPA/name/version, initializes chassis LEDs when configured, masks LASI interrupts and clears pending state, resets selected onboard devices, allocates a transaction IRQ, requests it with `gsc_asic_intr()`, writes the EIM to LASI’s IAR, calls `gsc_common_setup()`, walks child devices with `gsc_fixup_irqs()` using `lasi_choose_irq()`, and registers a sys-off power-off handler. `lasi_choose_irq()` maps known child `sversion` values to local IRQ bit numbers and calls `gsc_asic_assign_irq()`.

## State And Persistence
Per-chip state is the allocated `gsc_asic` and its local IRQ map. Hardware state includes masked/unmasked LASI interrupt bits, device reset writes, the IAR transaction target, LED register selection, and power control behavior. There is no removal path.

## Dependencies And Integration Points
LASI depends on GSC common interrupt infrastructure, PA-RISC PDC address validation, LED registration from `led.c`, reboot/sys-off infrastructure, and `parisc_device` child enumeration. It provides IRQs to onboard serial, LAN, SCSI, audio, PS/2, floppy, and other LASI-attached devices.

## Risks
The child IRQ mapping is a hard-coded table by `sversion` and one `hw_path` special case; new or misidentified devices receive no IRQ. Device reset writes are intentionally selective because firmware already initialized some devices. The power-off handler writes hardware and may not return. Error paths free allocated IRQ/state only for early failures before successful setup.

## Test Signals
Signals include LASI version log, successful parent IRQ request, child device IRQ assignment, IMR/IAR programming, functional onboard devices, LED registration on supported machines, and system power-off through LASI. Regression tests should cover Mirage/Electra LED address offsets and Gecko single-LED behavior.
