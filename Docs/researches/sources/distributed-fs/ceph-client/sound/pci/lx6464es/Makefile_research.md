# sources/distributed-fs/ceph-client/sound/pci/lx6464es/Makefile

## Purpose
This Makefile builds the Digigram LX6464ES ALSA PCI driver as the `snd-lx6464es` composite module.

## Important APIs, Types, and Functions
It declares `snd-lx6464es-y := lx6464es.o lx_core.o`, splitting the module between ALSA-facing PCI/PCM/control code and lower-level DSP/PLX mailbox code. `obj-$(CONFIG_SND_LX6464ES) += snd-lx6464es.o` ties the module to its kernel config symbol.

## Control Flow
Kbuild compiles `lx6464es.c` and `lx_core.c`, then links them into one module when `CONFIG_SND_LX6464ES` is enabled as built-in or module.

## State and Persistence
The Makefile has no runtime state. It preserves the source-to-module composition contract for LX6464ES.

## Dependencies and Integration Points
It depends on Kbuild composite-object syntax and `CONFIG_SND_LX6464ES`. The two object files share internal headers `lx6464es.h`, `lx_core.h`, and `lx_defs.h`.

## Risks
Missing either object breaks linkage: `lx6464es.o` needs DSP/IRQ helpers from `lx_core.o`, and `lx_core.o` needs `struct lx6464es` from the shared header. Adding future source files requires updating this list.

## Test Signals
A kernel build with `CONFIG_SND_LX6464ES=m/y` should produce/link `snd-lx6464es` without unresolved `lx_*` symbols. Disabling the config should omit the module.
