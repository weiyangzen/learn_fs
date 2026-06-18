# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-denverton.c

## Purpose

`pinctrl-denverton.c` supplies the static Intel Denverton SoC pin controller description consumed by the shared Intel pinctrl/GPIO core in `pinctrl-intel.c`. It maps Denverton pads 0-153 into named pins, muxable pin groups for UART0, UART1, UART2, and eMMC, two register communities, and ACPI/platform identifiers.

## Important APIs, Types, And Functions

The file is almost entirely declarative. It uses `PINCTRL_PIN()` for the pin table, `PIN_GROUP()` and `FUNCTION()` for mux exposure, `INTEL_GPP()` for pad-group metadata, and `INTEL_COMMUNITY_GPPS()` through `DNV_COMMUNITY()` to bind Denverton register offsets to each community. `dnv_soc_data` is the key exported payload, although it is static and reaches the core only through ACPI or platform match driver data. The driver entry points are `dnv_pinctrl_init()`, `dnv_pinctrl_exit()`, and the `platform_driver` with `.probe = intel_pinctrl_probe_by_hid`.

## Control Flow

During subsystem init, `platform_driver_register()` registers `denverton-pinctrl`. ACPI ID `INTC3000` or platform ID `denverton-pinctrl` carries `&dnv_soc_data`. Probe calls `intel_pinctrl_probe_by_hid()`, which fetches match data and calls the shared core. The core then maps community BARs, reads pad register bases and hardware capabilities, registers pinctrl and GPIO chips, and installs PM handling.

## State And Persistence

This file owns no mutable runtime state. Its static tables define North pins 0-40 and South pins 41-153, with pad groups split by hardware GPP boundaries. Runtime register state, GPIO ownership, IRQ masks, and suspend/resume pad context are allocated and maintained by `pinctrl-intel.c`. Denverton uses `subsys_initcall`, so registration occurs early enough for dependent devices that need GPIO/pinmux during boot.

## Dependencies And Integration Points

The driver depends on Linux platform, ACPI/module, PM, and pinctrl headers, and imports the `PINCTRL_INTEL` namespace. Integration is through the common Intel core's `intel_pinctrl_probe_by_hid()` and `intel_pinctrl_pm_ops`. The Denverton-specific register offsets are `DNV_PAD_OWN`, `DNV_PADCFGLOCK`, `DNV_HOSTSW_OWN`, `DNV_GPI_IS`, and `DNV_GPI_IE`.

## Risks

The main risk is table accuracy. A wrong pin number, mode array, pad-group range, GPIO base, or ACPI/platform ID would cause muxing, GPIO numbering, ownership checks, or interrupts to address the wrong pad. UART0 and UART2 use per-pin mode arrays, so array ordering must match the pin arrays exactly. Community boundaries also affect MMIO BAR selection and interrupt register indexing.

## Test Signals

Useful signals are successful probe on `INTC3000`, visible pin names and groups in pinctrl debugfs, UART/eMMC mux selection through pinctrl consumers, GPIO line enumeration across the expected ranges, and working shared IRQ delivery for Denverton GPPs. Suspend/resume should preserve active kernel-owned GPIO and mux state through the common PM callbacks.
