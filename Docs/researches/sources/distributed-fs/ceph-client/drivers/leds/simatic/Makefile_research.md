<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/Makefile

Purpose: This Makefile maps SIMATIC LED Kconfig symbols to object files.

Important mappings: `CONFIG_LEDS_SIEMENS_SIMATIC_IPC` builds `simatic-ipc-leds.o`. Each GPIO hardware family builds `simatic-ipc-leds-gpio-core.o` plus its board-specific lookup-table wrapper: Apollo Lake, F7188x, or Elkhart Lake.

Control flow and dependencies: The object grouping means the common GPIO probe/remove helpers are linked into every selected GPIO variant module, while board-specific modules contribute pin mappings and platform-driver registration. There is no runtime control flow in this file.

Risks and test signals: Selecting more than one GPIO family builds multiple copies of `simatic-ipc-leds-gpio-core.o` into separate modules, which is intentional because the helper exports GPL symbols. Verify module link names and soft dependencies for each variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/Makefile -->
