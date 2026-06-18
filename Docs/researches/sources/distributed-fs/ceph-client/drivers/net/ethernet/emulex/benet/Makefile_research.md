# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/Makefile

Purpose: defines the kbuild object composition for the Emulex/ServerEngines BladeEngine `be2net` network driver.

Important APIs/types/functions: `obj-$(CONFIG_BE2NET) += be2net.o` declares the final built-in or module object. `be2net-y := be_main.o be_cmds.o be_ethtool.o be_roce.o` lists the component objects linked into `be2net.o`.

Control flow: when kbuild enters the directory with `CONFIG_BE2NET` enabled, it compiles the four component source files and links them into `be2net.o`. As a module, that object becomes `be2net.ko`; as built-in, it is folded into the kernel image.

State and persistence behavior: no runtime state. The object list is deterministic and controlled by `.config` only through `CONFIG_BE2NET`; this Makefile does not conditionally include or exclude HWMON/chipset objects, so those variations are handled inside source via preprocessor conditionals.

Dependencies/integration points: depends on `benet/Kconfig` for `CONFIG_BE2NET` and on source files `be_main.c`, `be_cmds.c`, `be_ethtool.c`, and `be_roce.c`. The resulting object uses shared headers such as `be.h`, `be_hw.h`, and `be_roce.h`.

Risks: any missing component object breaks the whole driver build. New functionality added in separate source files must be appended to `be2net-y`; otherwise it will not link. Since all current components are always linked, source-level conditionals must correctly guard optional HWMON, RoCE, and chipset behavior.

Test signals: run `make M=drivers/net/ethernet/emulex/benet` or a full kernel build with `CONFIG_BE2NET=m/y`, verify `be2net.o` links all four objects, and inspect `modinfo be2net.ko` for expected module metadata from the implementation.
