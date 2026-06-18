# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/Makefile

## Purpose
This Makefile is the top-level build hook for Netronome Ethernet drivers. It descends into the `nfp/` subdirectory when `CONFIG_NFP` is enabled.

## Important entries
The single functional line is `obj-$(CONFIG_NFP) += nfp/`, which makes the complete Netronome NFP driver subtree conditional on the base Kconfig symbol.

## Control flow
During kbuild, if `CONFIG_NFP` is unset the subtree is skipped. If it is built-in or modular, kbuild enters `netronome/nfp/` and uses that directory's Makefile to assemble `nfp.o`.

## State and persistence
The file carries no runtime state. Build state is determined entirely by `CONFIG_NFP`.

## Dependencies and integration points
It integrates the vendor directory with kbuild and the `netronome/nfp/Makefile`. It depends on the Kconfig symbol defined in the sibling Kconfig file.

## Risks and edge cases
Because the file only gates the subtree, any incorrect dependency handling must be fixed in Kconfig or the nested Makefile. Removing or renaming this entry would silently exclude all NFP objects from builds even if Kconfig enables them.

## Test signals
Useful signals are kbuild inclusion/exclusion checks with `CONFIG_NFP=n/m/y`, verifying that `nfp/` objects are absent when disabled and included in the expected module or built-in image when enabled.
