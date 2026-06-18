# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/Makefile

## Purpose
This Makefile wires Toshiba Ethernet Kconfig symbols to built objects. It builds the PS3 Gelic composite driver, optionally adds its wireless component, and builds the Toshiba TC35815 driver.

## Important APIs, Types, And Functions
The key build variables are `obj-$(CONFIG_GELIC_NET)`, `gelic_wireless-$(CONFIG_GELIC_WIRELESS)`, `ps3_gelic-objs`, and `obj-$(CONFIG_TC35815)`.

`ps3_gelic-objs` always includes `ps3_gelic_net.o` when `CONFIG_GELIC_NET` selects the composite object. It appends `$(gelic_wireless-y)`, which resolves to `ps3_gelic_wireless.o` when `CONFIG_GELIC_WIRELESS=y`.

`obj-$(CONFIG_TC35815)` adds `tc35815.o` as built-in or module according to the tristate value.

## Control Flow
During kernel build evaluation, `CONFIG_GELIC_NET=y` links `ps3_gelic.o` into built-in objects; `CONFIG_GELIC_NET=m` builds it as a module. `ps3_gelic.o` is composed from `ps3_gelic_net.o` plus optional wireless support. `CONFIG_TC35815` independently controls `tc35815.o`.

## State And Persistence Behavior
The Makefile has no runtime state. Its persistent effect is build output selection based on `.config`.

## Dependencies And Integration Points
This file is the build companion to `drivers/net/ethernet/toshiba/Kconfig`. It depends on that file to restrict invalid symbol combinations. It integrates with the kernel kbuild composite-object convention where `<module>-objs` lists member objects for a module or built-in composite.

## Risks And Edge Cases
Because `GELIC_WIRELESS` is bool, `gelic_wireless-y` only appends wireless code when built-in to the composite object; this matches the Kconfig dependency on `GELIC_NET`. If `GELIC_WIRELESS` were ever changed to tristate, this Makefile would need adjustment to handle `m` semantics correctly.

The PS3 Gelic module name is `ps3_gelic`, not `ps3_gelic_net`, so packaging and module-loading tests should use the composite name.

## Test Signals
Build matrix checks should confirm `CONFIG_GELIC_NET=m` produces `ps3_gelic.ko`, `CONFIG_GELIC_WIRELESS=y` includes `ps3_gelic_wireless.o` in that composite, `CONFIG_GELIC_WIRELESS=n` omits it, and `CONFIG_TC35815=m` produces `tc35815.ko`.
