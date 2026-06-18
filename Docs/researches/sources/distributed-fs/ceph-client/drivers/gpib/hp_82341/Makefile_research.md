# sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/Makefile

Purpose: builds the HP 82341 adapter module when `CONFIG_GPIB_HP82341` is enabled. The declared object is `hp_82341.o`.

Important build API: `obj-$(CONFIG_GPIB_HP82341) += hp_82341.o` maps the Kconfig option to its adapter object. This file only covers build inclusion; the implementation is outside this work item.

Control flow and integration: the module is expected to integrate with the common GPIB registration layer like the other board drivers and likely depends on shared controller helpers, but this Makefile does not expose which callbacks or hardware core are used.

State and persistence: no runtime state. Its only effect is whether the HP82341 board driver is compiled.

Dependencies: Kconfig should ensure common GPIB support and any HP82341-specific bus/helper dependencies are selected.

Risks: the object name uses an underscore (`hp_82341.o`) while the directory name is `hp_82341`; any source rename mismatch would break the build. Since no composite object list is present, all implementation must be in a single matching C file.

Test signals: build with `CONFIG_GPIB_HP82341=m`; verify `hp_82341.o` exists, module links against required common symbols, and load/unload registration succeeds.
