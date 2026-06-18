# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/Makefile

## Purpose
This Makefile maps Nuvoton pinctrl Kconfig symbols to their corresponding object files. It is the build glue that includes family-specific and common pinctrl drivers in the kernel build.

## Important APIs, types, and functions
The key entries are `obj-$(CONFIG_PINCTRL_WPCM450) += pinctrl-wpcm450.o`, `obj-$(CONFIG_PINCTRL_NPCM7XX) += pinctrl-npcm7xx.o`, `obj-$(CONFIG_PINCTRL_NPCM8XX) += pinctrl-npcm8xx.o`, `obj-$(CONFIG_PINCTRL_MA35) += pinctrl-ma35.o`, and `obj-$(CONFIG_PINCTRL_MA35D1) += pinctrl-ma35d1.o`.

## Control flow
There is no runtime control flow. Kbuild expands each `obj-$(CONFIG_...)` according to the configured symbol value. For MA35D1, the Kconfig relationship causes both the common `pinctrl-ma35.o` and SoC-specific `pinctrl-ma35d1.o` objects to be included when MA35D1 support is enabled.

## State and persistence behavior
The Makefile does not store runtime state. Its persistent effect is in build artifacts: enabled objects become built-in or module objects according to their Kconfig symbol type and value. Since `PINCTRL_MA35` and `PINCTRL_MA35D1` are bools, the MA35 objects are built-in rather than modules.

## Dependencies and integration points
This file integrates with the local Kconfig and with the wider Linux Kbuild system. The object names correspond directly to source files in the same directory. It is especially coupled to the MA35 split, where `pinctrl-ma35d1.c` calls functions implemented in `pinctrl-ma35.c`.

## Risks
The main risk is symbol/object drift. If Kconfig selects a symbol but the Makefile omits the object, probe entry points or common helpers will be missing. If an object is tied to the wrong symbol, unrelated platforms may build unused code or fail when dependencies are absent. The MA35 common object must stay tied to the hidden common symbol rather than only the MA35D1 wrapper if additional MA35 variants are added.

## Test signals
Run Kbuild with each Nuvoton config enabled and disabled. For MA35D1, link validation should prove that `ma35_pinctrl_probe()`, `ma35_pinctrl_suspend()`, and `ma35_pinctrl_resume()` resolve from `pinctrl-ma35.o` when `pinctrl-ma35d1.o` is included.
