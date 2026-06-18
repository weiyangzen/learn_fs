<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/Makefile

## Purpose

`mux/Makefile` maps Type-C mux Kconfig symbols to object files.

## Important APIs, Types, and Functions

Each `obj-$(CONFIG_...) += ...o` entry corresponds to a chip or platform driver: `fsa4480.o`, `gpio-sbu-mux.o`, `pi3usb30532.o`, `intel_pmc_mux.o`, `it5205.o`, `nb7vpq904m.o`, `ps883x.o`, `ptn36502.o`, `tusb1046.o`, and `wcd939x-usbss.o`.

## Control Flow

The build system includes an object only when the associated config is enabled. There is no runtime logic.

## State and Persistence Behavior

No runtime state or persistence exists. The file only controls build artifacts.

## Dependencies and Integration Points

It integrates the Kconfig menu with kbuild and module generation for the Type-C mux directory.

## Risks and Test Signals

Risks are stale object mappings when Kconfig symbols or filenames change. Test signals are successful built-in and module builds for each symbol and confirming module names match Kconfig help text where documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/Makefile -->
