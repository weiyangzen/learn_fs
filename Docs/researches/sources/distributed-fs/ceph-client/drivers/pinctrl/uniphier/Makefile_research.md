# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/Makefile

## Purpose

This Makefile maps UniPhier pinctrl Kconfig symbols to Kbuild objects. It always builds the shared UniPhier pinctrl core when the directory is included, and conditionally builds one object per supported UniPhier SoC family.

## Important APIs, Types, and Functions

The key unconditional rule is `obj-y += pinctrl-uniphier-core.o`. Conditional rules map `CONFIG_PINCTRL_UNIPHIER_LD4`, `PRO4`, `SLD8`, `PRO5`, `PXS2`, `LD6B`, `LD11`, `LD20`, `PXS3`, and `NX1` to their corresponding `pinctrl-uniphier-*.o` objects. There are no C functions here; the file's interface is the Kbuild object list.

## Control Flow

When Kbuild descends into this directory, it compiles the core object and any SoC object whose Kconfig symbol expands to `y`. Because the Kconfig symbols are bools, this Makefile does not produce modules for UniPhier pinctrl; selected objects become built-in.

## State and Persistence

Persistent state is limited to kernel build artifacts. Runtime pinctrl state is owned by the compiled C drivers and hardware registers, not by this file.

## Dependencies and Integration Points

It depends on `drivers/pinctrl/uniphier/Kconfig` defining the listed symbols and on source files with matching names. It integrates with the top-level pinctrl build and with the shared UniPhier core that SoC-specific objects use for common registration and pinconf behavior.

## Risks

The unconditional `obj-y` core rule assumes directory inclusion is already gated by higher-level Kbuild/Kconfig. If a SoC symbol is added in Kconfig but not here, the option will not compile its driver. If a rule points at the wrong object, the build fails or probes for that SoC disappear. The lack of module rules is intentional but should be considered if future symbols become tristate.

## Test Signals

Build UniPhier configurations selecting each SoC option and confirm the matching object appears in the build log. Verify that the core object is present whenever any UniPhier pinctrl driver is built. Cross-check Kconfig and Makefile symbol lists whenever new UniPhier SoC support is added.
