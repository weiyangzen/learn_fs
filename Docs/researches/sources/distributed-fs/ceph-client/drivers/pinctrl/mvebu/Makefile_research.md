# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/Makefile

## Purpose
This Makefile maps MVEBU pinctrl Kconfig symbols to the shared core object and SoC-specific pinctrl driver objects.

## Important APIs, Types, and Entries
- `obj-$(CONFIG_PINCTRL_MVEBU) += pinctrl-mvebu.o` builds the shared legacy MVEBU core.
- SoC entries build Dove, Kirkwood, Armada 370/375/38x/39x/AP806/CP110/XP, Armada 37xx, Orion, and AC5 objects according to their Kconfig symbols.

## Control Flow
There is no runtime control flow. Kbuild uses the evaluated `CONFIG_*` variables to include objects.

## State and Persistence
Build state is held in `.config`. No runtime state is represented here.

## Dependencies and Integration Points
It must stay synchronized with `Kconfig` and source filenames. Most listed SoC drivers depend on `pinctrl-mvebu.o`; Armada 37xx is included separately by its own symbol.

## Risks
If a SoC symbol is enabled without the expected shared core selection, link failures can occur; current Kconfig selections handle the legacy drivers. Formatting differences are benign, but object naming drift would break builds.

## Test Signals
Build with each `CONFIG_PINCTRL_*` symbol enabled and disabled, and confirm object inclusion with Kbuild verbose output or `make drivers/pinctrl/mvebu/`.
