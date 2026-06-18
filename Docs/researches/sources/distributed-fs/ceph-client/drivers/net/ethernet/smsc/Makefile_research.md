# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/Makefile

## Purpose
This Makefile maps SMSC Ethernet Kconfig symbols to the driver objects built from this directory.

## Important APIs, Types, and Data
- `obj-$(CONFIG_SMC91X) += smc91x.o`
- `obj-$(CONFIG_EPIC100) += epic100.o`
- `obj-$(CONFIG_SMSC9420) += smsc9420.o`
- `obj-$(CONFIG_SMSC911X) += smsc911x.o`

## Control Flow
Kbuild expands each `obj-$()` assignment according to the final kernel configuration. A built-in `y` includes the object in vmlinux or the parent object list; an `m` builds it as a module; an unset symbol omits it.

## State and Persistence
There is no runtime state. The file affects only the build graph derived from `.config`.

## Dependencies and Integration Points
It consumes symbols declared in `smsc/Kconfig` and integrates the four SMSC drivers into the kernel's recursive build system.

## Risks and Edge Cases
- A mismatch between Kconfig symbol names and object rules would silently skip a selected driver.
- Adding a new source file for an existing module would require object aggregation rather than a single `foo.o` rule.
- The ordering is simple and has no conditional subdirectories, so future multi-file drivers need careful Kbuild expansion.

## Test Signals
Build with each symbol as `m` and `y`, verify expected `.o` or `.ko` outputs, and confirm no object is built when the symbol is unset.
