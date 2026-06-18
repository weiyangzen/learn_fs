# sources/distributed-fs/ceph-client/drivers/misc/cb710/Makefile

Purpose: defines object composition for the ENE CB710 cardreader driver.

Important APIs, types, and functions: `ccflags-$(CONFIG_CB710_DEBUG) := -DDEBUG` enables `dev_dbg()` output when debugging is selected. `obj-$(CONFIG_CB710_CORE) += cb710.o` builds the aggregate module. `cb710-y := core.o sgbuf2.o` always includes core PCI/platform-slot logic and SG iterator helpers; `cb710-$(CONFIG_CB710_DEBUG) += debug.o` adds register dumping.

Control flow: no runtime control flow; Kbuild combines objects based on Kconfig.

State and persistence: no runtime state. The Makefile controls compilation products.

Dependencies and integration points: paired with `cb710/Kconfig` and source files in the same directory. Child drivers link against exported symbols from `core.o` and `sgbuf2.o`.

Risks: debug-only `debug.o` means calls to `cb710_dump_regs()` must be guarded or only present when `CONFIG_CB710_DEBUG` exports it. Object composition must stay aligned with exported symbols used by child drivers.

Test signals: verify builds with `CONFIG_CB710_CORE=m`, `CONFIG_CB710_DEBUG=y/n`, and link checks for exported CB710 helpers.
