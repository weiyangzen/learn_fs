# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/Makefile

Purpose: maps HyperBus Kconfig symbols to object files.

Important APIs/types/functions: builds `hyperbus-core.o` for `CONFIG_MTD_HYPERBUS`, `hbmc-am654.o` for `CONFIG_HBMC_AM654`, and `rpc-if.o` for `CONFIG_RPCIF_HYPERBUS`.

Control flow: build-system only. The core can be built independently when the framework is enabled; controller objects are included only for selected drivers.

State and persistence: no runtime state.

Dependencies/integration: consumed by Kbuild under `drivers/mtd/hyperbus`; must stay synchronized with Kconfig symbol names and source filenames.

Risks: stale symbol/object names silently omit driver code or break builds. Controller objects depend on the core export symbols, so configurations should include core when controllers are enabled through Kconfig nesting.

Test signals: compile each symbol as built-in and module where allowed; verify linked modules contain the expected platform drivers and exported core symbols resolve.
