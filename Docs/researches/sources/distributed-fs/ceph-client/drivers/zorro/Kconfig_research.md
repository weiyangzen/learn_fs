<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/zorro/Kconfig

## Purpose
This Kconfig fragment controls the optional Zorro device-name database for Amiga Zorro bus support.

## Important APIs, types, and functions
It defines `CONFIG_ZORRO_NAMES`, a boolean depending on `ZORRO`.

## Control flow
At configuration time, enabling the symbol causes kbuild to include `names.o` and generated device-name tables.

## State and persistence
The only persistent state is the selected `.config` value. Runtime names are initialized during boot and the init-only database can be freed afterward.

## Dependencies and integration points
It integrates with the Zorro bus core and the `drivers/zorro/Makefile` rule that generates `devlist.h` from `zorro.ids`.

## Risks and test signals
Risks are hidden name support when users expect descriptive `/proc/iomem` output, or extra image size in constrained configs. Test signals include `CONFIG_ZORRO_NAMES=y/n`, Amiga Zorro boot logs, and generated header builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/Kconfig -->
