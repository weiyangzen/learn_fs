# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel.h

## Purpose

`pinctrl-intel.h` defines the data contract between Intel SoC-specific pinctrl drivers and the shared Intel core. It also exposes the core probe, ACPI selection, group/function, GPIO range, community lookup, and PM symbols used by companion drivers.

## Important APIs, Types, And Functions

Key types are `struct intel_pingroup`, `struct intel_function`, `struct intel_padgroup`, `struct intel_community`, `struct intel_pinctrl_soc_data`, `struct intel_pinctrl_context`, and `struct intel_pinctrl`. Key macros are `INTEL_GPP()`, `INTEL_COMMUNITY_GPPS()`, `INTEL_COMMUNITY_SIZE()`, `PIN_GROUP()`, `PIN_GROUP_GPIO()`, and `FUNCTION()`. Special GPIO base values are `INTEL_GPIO_BASE_ZERO`, `INTEL_GPIO_BASE_NOMAP`, and `INTEL_GPIO_BASE_MATCH`. Feature bits include debounce, 1K pull-down support, GPIO hardware info, PWM, blink, EXP, and 3-bit PAD_OWN.

## Control Flow

The header itself has no control flow, but its declarations drive core behavior. SoC files instantiate `intel_pinctrl_soc_data`; probe helpers pass that data to `intel_pinctrl_probe()`. The core then interprets communities, pad groups, pin groups, and functions according to these structure fields and macros.

## State And Persistence

The header separates immutable SoC templates from runtime state. SoC templates are `const` arrays. `struct intel_pinctrl` is mutable runtime state with copied communities, MMIO pointers, gpiochip, pinctrl device, spinlock, PM context, and IRQ. `struct intel_pinctrl_context` is the saved suspend/resume container.

## Dependencies And Integration Points

The header depends on kernel pinctrl, gpio, irq, PM, spinlock, bits, and array-size definitions. It is included by modern Intel SoC drivers and by special cases such as Lynxpoint that reuse common helper APIs. It exports symbols in namespace `PINCTRL_INTEL`, requiring module users to import that namespace.

## Risks

Macro misuse can silently build wrong static tables. `PIN_GROUP()` uses compile-time selection to treat a mode argument as either a scalar or an array; passing an expression with unexpected constant-ness could choose the wrong field. `INTEL_GPP()` sizes are derived from inclusive start/end values, so off-by-one errors are easy. The meaning of special GPIO bases must be preserved because many SoC files depend on NOMAP or forced-zero behavior.

## Test Signals

Compile coverage is important because many table definitions rely on macro typing. Runtime validation comes indirectly from every SoC driver: correct group counts, function names, GPIO ranges, community lookup, PM callbacks, and namespace imports all exercise this header's contract.
