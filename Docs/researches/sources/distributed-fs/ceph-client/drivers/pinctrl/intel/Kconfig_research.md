# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/Kconfig

## Purpose
Defines the Kconfig menu and build-time feature symbols for Intel pinctrl/GPIO drivers. It exposes user-selectable platform drivers and the shared `PINCTRL_INTEL` core dependency used by many newer Intel PCH and SoC pin controllers.

## Important APIs, Types, and Functions
This is Kconfig data rather than C code. Important symbols include `PINCTRL_BAYTRAIL`, `PINCTRL_CHERRYVIEW`, `PINCTRL_LYNXPOINT`, `PINCTRL_INTEL`, `PINCTRL_INTEL_PLATFORM`, `PINCTRL_ALDERLAKE`, `PINCTRL_BROXTON`, `PINCTRL_CANNONLAKE`, `PINCTRL_CEDARFORK`, and later platform symbols such as Elkhart Lake, Gemini Lake, Ice Lake, Meteor Lake, Meteor Point, Sunrise Point, and Tiger Lake. `PINCTRL_INTEL` selects `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, `GPIOLIB`, and `GPIOLIB_IRQCHIP`.

## Control Flow
During kernel configuration, the menu is visible when `(ACPI && X86) || COMPILE_TEST` is true. Selecting a platform driver selects `PINCTRL_INTEL` where applicable. `source "drivers/pinctrl/intel/Kconfig.tng"` includes additional Intel Tangier/Merrifield/Moorefield configuration.

## State and Persistence Behavior
The selected symbols persist in `.config` and determine which objects are compiled built-in or as modules. The hidden `PINCTRL_INTEL` symbol centralizes common framework dependencies for descriptor-style Intel drivers.

## Dependencies and Integration Points
Integrates with the kernel Kconfig system, ACPI/X86 platform discovery, compile-test builds, the Intel pinctrl Makefile, and the Linux pinctrl/GPIO subsystems. Help text identifies the SoC/PCH families served by each option.

## Risks
Missing `select PINCTRL_INTEL` or framework dependencies causes link or runtime registration failures. Overly narrow dependencies can block compile testing; overly broad ones can expose drivers on unsupported systems. Help text and platform lists can drift from ACPI IDs implemented in the C files.

## Test Signals
`olddefconfig` and `allyesconfig`/`allmodconfig` on X86 and COMPILE_TEST, object inclusion matching selected symbols, no unmet dependency warnings, and successful module builds for each listed platform are useful signals.
