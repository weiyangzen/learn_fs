# sources/distributed-fs/ceph-client/sound/isa/es1688/Makefile

## Purpose

This Makefile builds the ESS ES1688/ES688 ALSA ISA modules. It separates the reusable ES1688 low-level library from the card driver and links the library into both the normal ES1688 driver and the Gravis UltraSound Extreme driver.

## Important APIs, Types, and Functions

- `snd-es1688-lib-y := es1688_lib.o` defines the low-level library module object.
- `snd-es1688-y := es1688.o` defines the ES1688 card driver object.
- `obj-$(CONFIG_SND_ES1688) += snd-es1688.o snd-es1688-lib.o` builds both card and library modules for ES1688.
- `obj-$(CONFIG_SND_GUSEXTREME) += snd-es1688-lib.o` reuses the low-level library for GUS Extreme support.

## Control Flow

Kbuild compiles and links the ES1688 card and library objects according to selected config symbols. The library object can be built without the standalone ES1688 card module when another driver needs its exported functions.

## State and Persistence Behavior

The Makefile has no runtime state. Its persistent effect is build composition and symbol availability for drivers that depend on `es1688_lib.o`.

## Dependencies and Integration Points

It depends on Kbuild and `CONFIG_SND_ES1688`/`CONFIG_SND_GUSEXTREME`. The exported functions in `es1688_lib.c` form the integration point for the standalone and GUS Extreme paths.

## Risks and Edge Cases

Because two configs can reference `snd-es1688-lib.o`, build changes must avoid duplicate or missing module-object definitions. Removing the library from either object list can break external users of its exported symbols.

## Test Signals

Build testing should cover `CONFIG_SND_ES1688=m`, `CONFIG_SND_GUSEXTREME=m`, and both enabled together, confirming the library object is produced and linked without duplicate symbol issues.
