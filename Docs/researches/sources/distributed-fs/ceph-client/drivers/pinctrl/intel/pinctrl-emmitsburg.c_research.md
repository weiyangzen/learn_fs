# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-emmitsburg.c

## Purpose

`pinctrl-emmitsburg.c` provides the Emmitsburg PCH pin map for the shared Intel pinctrl/GPIO core. It covers 262 pins across server-oriented eSPI, SPI, SMBus, SATA, JTAG, GBE/NCSI, CPU/platform management, and NAC groups.

## Important APIs, Types, And Functions

The important payload is `ebg_soc_data`, containing `ebg_pins` and five community descriptors. `EBG_COMMUNITY()` binds Emmitsburg-specific register offsets into `struct intel_community`. The driver table matches ACPI HID `INTC1071`, and the platform driver calls `intel_pinctrl_probe_by_hid()`.

## Control Flow

`module_platform_driver()` registers `emmitsburg-pinctrl`. ACPI matching supplies `&ebg_soc_data`. The common Intel probe copies the community templates, maps one BAR per community, discovers optional capabilities from hardware, creates pad groups from the provided `INTEL_GPP()` entries, registers pinctrl and GPIO, and wires the shared interrupt handler.

## State And Persistence

The file has no writable state after module load. It declares GPP ranges and GPIO bases: communities cover pins 0-65, 66-111, 112-145, 146-183, and 184-261. Suspend/resume state for active pads, interrupt masks, and host ownership registers is held in the core driver's `intel_pinctrl_context`.

## Dependencies And Integration Points

Emmitsburg depends on `pinctrl-intel.h` macros and the `PINCTRL_INTEL` namespace. Its ACPI integration is HID-based, not UID-based. Hardware integration points include server PCH GPIO ownership, eSPI/SPI, GBE, NCSI, SMBus, SATA sideband, and CPU error/reset signaling.

## Risks

This is a large server pin table where an off-by-one range can affect many GPIO numbers. The community names in comments are not executed, so correctness depends on the numeric `INTEL_GPP()` ranges and GPIO bases. Missing function/group tables mean this driver exposes GPIO/pad data but not named alternate-function mux groups through the generic pinmux function list.

## Test Signals

Probe on `INTC1071` should produce a gpiochip with ranges aligned to GPP_A/B/S, GPP_C/D, GPP_E/JTAG, GPP_H/J, and GPP_I/L/M/N. GPIO IRQ tests should confirm `EBG_GPI_IS`/`EBG_GPI_IE` offsets. Debugfs should show the expected pin names, ownership state, lock state, and ACPI mode flags.
