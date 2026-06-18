# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel-platform.c

## Purpose

`pinctrl-intel-platform.c` is a generic firmware-described Intel PCH pinctrl/GPIO driver for ACPI HID `INTC105F`. Instead of hard-coding pin tables, it builds `struct intel_pinctrl_soc_data` from device properties and child nodes.

## Important APIs, Types, And Functions

`intel_platform_pinctrl_prepare_pins()` allocates pin names and descriptors, replacing `-` with `_` for name normalization. `intel_platform_pinctrl_prepare_group()` reads child properties `intc-gpio-group-name` and `intc-gpio-pad-count`, builds pins, and fills an `intel_padgroup`. `intel_platform_pinctrl_prepare_community()` reads register offsets from device properties, allocates one pad group per child node, and sets common community fields. `intel_platform_pinctrl_prepare_soc_data()` currently creates one community per platform device. `intel_platform_pinctrl_probe()` allocates generated SoC data and calls `intel_pinctrl_probe()`.

## Control Flow

On probe, the driver allocates an empty `intel_pinctrl_soc_data`, reads firmware properties, creates pin descriptors in child-node order, creates pad groups with `INTEL_GPIO_BASE_MATCH`, and then delegates to the shared Intel core. The core treats the generated structures the same way it treats static SoC descriptors.

## State And Persistence

All generated descriptors are device-managed allocations tied to the platform device lifetime. The generated pin table is persistent for the driver's lifetime but not global static data. Runtime GPIO, IRQ, pinmux, and PM state is still owned by `pinctrl-intel.c`.

## Dependencies And Integration Points

This file depends heavily on firmware property correctness: ownership, lock, host software ownership, interrupt status, and interrupt enable offsets all come from device properties. It also depends on child nodes for group names and pad counts. It integrates with `devm_kasprintf_strarray()`, `fwnode` child iteration, ACPI match `INTC105F`, and the common Intel core.

## Risks

Malformed firmware can fail probe or create unusable pin maps. Version 1.0 assumes only one community per device node, so multi-community firmware must be represented as multiple devices or future code changes. `devm_krealloc_array()` grows the pin descriptor array by absolute pin number; unexpected large pad counts can increase memory use. Name normalization changes hyphens to underscores, which is desirable for consistency but is still visible ABI in debug and consumer references.

## Test Signals

Tests should exercise missing properties, zero child nodes, multiple child groups, name normalization, and correct GPIO base matching. On real hardware, the generated line names and line count should match firmware. GPIO input/output and IRQ tests verify that property-provided register offsets are correct.
