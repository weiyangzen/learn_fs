# sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/Makefile

## Purpose
This Makefile maps the LiteX Ethernet Kconfig selection to the object built by Kbuild.

## Important Entries
The only build rule is `obj-$(CONFIG_LITEX_LITEETH) += litex_liteeth.o`. When the symbol is `y`, the object is built in; when `m`, it is built as a module; when unset, it is omitted.

## Control Flow
Kbuild expands `obj-*` variables after configuration. This file has no conditional subdirectories or composite objects, so the build path is direct from `CONFIG_LITEX_LITEETH` to `litex_liteeth.c`.

## State And Persistence
Build state is entirely driven by `.config` and generated Kbuild metadata. No runtime state is introduced here.

## Dependencies And Integration Points
It integrates with `litex/Kconfig`, the parent Ethernet Makefile that descends into this directory, and the `litex_liteeth.c` module metadata.

## Risks
The file is intentionally simple. The main risk is drift: renaming the source file or adding companion objects without updating this rule would break the build. Any future split into multiple objects would require a composite `litex_liteeth-y` style rule.

## Test Signals
Build with `CONFIG_LITEX_LITEETH=y`, `m`, and unset. Check that module naming and dependency metadata match the driver source.
