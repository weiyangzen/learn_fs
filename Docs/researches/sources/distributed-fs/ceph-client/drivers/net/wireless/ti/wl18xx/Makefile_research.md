# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/Makefile

## Purpose
Defines the object composition for the wl18xx chip-family module.

## Important APIs, types, and functions
- `wl18xx-objs` lists `main.o acx.o tx.o io.o debugfs.o scan.o cmd.o event.o`.
- `obj-$(CONFIG_WL18XX) += wl18xx.o` links those objects into the wl18xx module or builtin object.

## Control flow
No runtime flow. Build flow aggregates the listed implementation files into the lower-driver module selected by Kconfig.

## State and persistence behavior
No runtime state. Build output depends on `CONFIG_WL18XX`.

## Dependencies and integration points
Integrates with kbuild and the wlcore module selected by `wl18xx/Kconfig`. The object list is the implementation boundary for WiLink 8-specific overrides.

## Risks and test signals
Omitting a new implementation object would compile-link fail when symbols are referenced, while stale objects can keep dead code in the module. Test with `make M=drivers/net/wireless/ti/wl18xx` or full kernel builds for module and builtin variants.
