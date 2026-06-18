# sources/distributed-fs/ceph-client/drivers/memstick/core/Makefile

Purpose: This Makefile maps MemoryStick core Kconfig symbols to compiled objects in the core directory.

Important APIs/types/functions: `obj-$(CONFIG_MEMSTICK) += memstick.o` builds the bus/core implementation. `obj-$(CONFIG_MS_BLOCK) += ms_block.o` builds the standard MemoryStick block driver. `obj-$(CONFIG_MSPRO_BLOCK) += mspro_block.o` builds the MemoryStick Pro block driver.

Control flow: Kbuild includes objects according to tristate values. If an option is modular, the corresponding object becomes part of a module; if built-in, it is linked into the kernel image.

State and persistence: There is no runtime state. Build products are determined by `.config`.

Dependencies and integration: Depends on symbols declared in `drivers/memstick/core/Kconfig` and on the top-level MemoryStick Makefile descending into `core/`.

Risks and test signals: Risks are build graph mistakes that omit core bus support or block drivers despite selected options. Test signals include all combinations of `MEMSTICK`, `MS_BLOCK`, and `MSPRO_BLOCK` as built-in/module where legal, plus module dependency checks ensuring block drivers can resolve exported core symbols.
