# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/Makefile

Purpose: connects the top-level Emulex Ethernet driver directory to the kernel build system by descending into the BladeEngine/be2net subdirectory when `CONFIG_BE2NET` is enabled.

Important APIs/types/functions: the only build rule is `obj-$(CONFIG_BE2NET) += benet/`, which makes the `benet` subdirectory conditional on the be2net Kconfig tristate.

Control flow: during kbuild, if `CONFIG_BE2NET=y`, objects in `benet/` are linked into the built-in kernel image; if `CONFIG_BE2NET=m`, the subdirectory builds a module; if unset, the subdirectory is skipped.

State and persistence behavior: no runtime state. Build selection is persisted in `.config` through `CONFIG_BE2NET`.

Dependencies/integration points: depends on `drivers/net/ethernet/emulex/benet/Makefile` to name the actual be2net object and component objects. It is reached from the parent networking drivers Makefile when the Emulex vendor directory is included.

Risks: because the directory is keyed directly to `CONFIG_BE2NET`, adding any other Emulex driver would require extending this Makefile. A mismatch between Kconfig symbols and this rule would silently omit builds.

Test signals: build with `CONFIG_BE2NET=y`, `m`, and unset; confirm `benet/` is visited only for enabled cases and that the final built-in object or module includes be2net components.
