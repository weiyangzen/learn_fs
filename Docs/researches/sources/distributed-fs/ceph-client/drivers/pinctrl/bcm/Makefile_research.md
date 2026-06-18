# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/Makefile

## Purpose
This Makefile maps Broadcom pinctrl Kconfig symbols to the object files compiled into the kernel or modules. It is the build glue for the Broadcom pinctrl subdirectory.

## Important APIs, types, and functions
The file uses standard kernel `obj-$(CONFIG_...) += ...` assignments. Notable mappings include `CONFIG_PINCTRL_BCM281XX` to `pinctrl-bcm281xx.o`, `CONFIG_PINCTRL_BCM2835` to `pinctrl-bcm2835.o`, `CONFIG_PINCTRL_BCM4908` to `pinctrl-bcm4908.o`, shared and SoC-specific BCM63xx objects, `CONFIG_PINCTRL_BRCMSTB` to `pinctrl-brcmstb.o`, `CONFIG_PINCTRL_BCM2712` to `pinctrl-brcmstb-bcm2712.o`, and iProc, Cygnus, NS, NSP, and NS2 drivers.

## Control flow
During kernel build, Kbuild expands each `obj-y`, `obj-m`, or empty assignment based on the resolved `.config`. Enabled built-in symbols compile into the built-in object list; module symbols compile as modules when the symbol is tristate and set to `m`.

## State and persistence behavior
The Makefile stores no runtime state. Its effect is persistent only in build outputs and depends entirely on `.config`.

## Dependencies and integration points
It integrates with the local Kconfig symbols and the Linux Kbuild system. It assumes each referenced object has a matching source file in the same directory and that symbol type matches whether modular builds are possible.

## Risks
A missing or misspelled object mapping causes an enabled driver not to build. A stale mapping to a removed source breaks builds. Referencing `CONFIG_PINCTRL_BCM2712` here while its Kconfig may be sourced elsewhere requires the broader Kconfig tree to define it consistently. Ordering is mostly not semantically significant, but shared objects such as `pinctrl-bcm63xx.o` must be selected when dependent variants need common code.

## Test signals
Build tests with representative configs should confirm each Kconfig symbol produces the intended object. `make W=1` or allmodconfig-style builds can catch stale object references. Comparing this file against local Kconfig symbols is a useful static consistency check.
