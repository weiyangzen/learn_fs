# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/Makefile

Purpose: this Makefile maps Broadcom Kconfig symbols to built objects and subdirectories. It is the build-system dispatch layer for all drivers under `drivers/net/ethernet/broadcom`.

Important APIs/types/functions: the file uses standard kernel `obj-$(CONFIG_...) += ...` assignments. The relevant ASP2 entry is `obj-$(CONFIG_BCMASP) += asp2/`, which delegates object construction to the `asp2/Makefile`. Other entries build single objects (`b44.o`, `tg3.o`, `bgmac.o`) or subdirectories (`genet/`, `bnx2x/`, `bnxt/`, `bnge/`).

Control flow: at build time, kbuild evaluates each `CONFIG_*` symbol and descends into enabled subdirectories or compiles enabled objects. Runtime control flow is unaffected except that unavailable objects cannot register their drivers.

State and persistence: no runtime state exists. The persistent input is the configured kernel `.config`; the output is object/module inclusion in the build tree.

Dependencies and integration points: this file integrates directly with `Kconfig` symbols and lower-level Makefiles, especially `broadcom/asp2/Makefile` for `CONFIG_BCMASP`. It must stay synchronized with file locations and module object names.

Risks: stale object names or missing directory entries cause drivers to disappear from builds despite enabled Kconfig symbols. For ASP2, the parent Makefile only delegates to `asp2/`; the child Makefile must define the actual module object. Test signals include `make M=drivers/net/ethernet/broadcom`, `CONFIG_BCMASP=m` module builds, and allmodconfig link coverage.
