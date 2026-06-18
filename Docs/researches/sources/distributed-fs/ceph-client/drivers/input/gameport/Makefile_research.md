# sources/distributed-fs/ceph-client/drivers/input/gameport/Makefile

This Makefile maps gameport Kconfig symbols to kernel objects. `CONFIG_GAMEPORT` builds the generic bus/core object `gameport.o`; `CONFIG_GAMEPORT_EMU10K1`, `CONFIG_GAMEPORT_FM801`, `CONFIG_GAMEPORT_L4`, and `CONFIG_GAMEPORT_NS558` build their corresponding hardware provider modules.

There are no functions or runtime state, but the file is an integration point between Kconfig and kbuild. It preserves the expected module names from help text: `gameport`, `emu10k1-gp`, `fm801-gp`, `lightning`, and `ns558`. The object list also defines link inclusion for built-in configurations, so core availability must line up with consumers that select or depend on `GAMEPORT`.

Risks are simple but high-impact: symbol/object mismatches cause missing modules, stale objects fail builds, and ordering mistakes could omit the generic core when only provider symbols are enabled. Test signals include `make drivers/input/gameport/`, `allmodconfig`, `allyesconfig`, and checking generated modules under `drivers/input/gameport`.
