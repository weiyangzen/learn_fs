# sources/distributed-fs/ceph-client/drivers/comedi/drivers/Makefile

## Purpose

This Makefile maps COMEDI Kconfig symbols to individual low-level driver objects and helper modules. It is the build manifest for standalone helpers, misc drivers, ISA, PCI, PCMCIA, USB, National Instruments shared support, common helper objects, and COMEDI tests.

## Important APIs, types, and functions

The important interface is Kbuild's `obj-$(CONFIG_...) += ...` syntax. `ccflags-$(CONFIG_COMEDI_DEBUG) := -DDEBUG` enables debug builds. Composite object lists such as `ni_routing-objs` define multi-object modules. The requested files are wired by entries such as `CONFIG_COMEDI_8255_PCI`, `CONFIG_COMEDI_ADDI_*`, `CONFIG_COMEDI_ADL_*`, `CONFIG_COMEDI_8255`, and `CONFIG_COMEDI_8255_SA`.

## Control Flow

During kernel build, Kbuild evaluates enabled COMEDI config symbols and includes the matching objects. Helper modules like `comedi_8254.o`, `comedi_isadma.o`, `comedi_8255.o`, and `addi_watchdog.o` are built only when their symbols are enabled. Bus-specific groups are organized by comments but all produce ordinary Kbuild object lists. The tests directory is included through `obj-$(CONFIG_COMEDI_TESTS) += tests/`.

## State and Persistence

There is no runtime state. The persistent behavior is the source-controlled build mapping from configuration to modules. The list determines which drivers can be compiled into the kernel or as modules and which shared helper objects are available to low-level drivers.

## Dependencies and Integration Points

This file integrates with COMEDI Kconfig definitions, Linux Kbuild, and source files under `drivers/comedi/drivers/`. Ordering generally does not impose runtime load order, but missing helper entries or wrong config symbols can cause unresolved symbols or silently unavailable drivers.

## Risks

The risk is build coverage and dependency drift. A driver using a shared helper must have the helper selectable through Kconfig and listed here. Renames must update both Kconfig and Makefile entries. Composite modules such as `ni_routing` require all component paths to stay in sync. Conditional I/O-port-only drivers must still compile correctly under configurations that disable port I/O.

## Test Signals

Signals include `make drivers/comedi/drivers/` for multiple config sets, `COMEDI_DEBUG` builds showing `-DDEBUG`, all enabled requested objects appearing in build output, no unresolved symbols for `addi_watchdog` or `comedi_8255`, and successful `modinfo`/module load for selected low-level drivers.
