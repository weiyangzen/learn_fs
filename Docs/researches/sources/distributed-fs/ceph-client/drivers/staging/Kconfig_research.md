<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/Kconfig

Purpose: defines the top-level `STAGING` Kconfig menu and sources all staging driver submenus in this kernel tree.

Important APIs/types/functions: `menuconfig STAGING` is a bool gate with a warning help text about driver quality, kernel taint, and unstable userspace interfaces. Inside `if STAGING`, it sources RTL8723BS, Octeon, IIO, SM750FB, NVEC, media, FBTFT, MOST, Greybus, VC04 services, axis-fifo, and vme_user Kconfig files.

Control flow: Kconfig visibility flows from `STAGING`; none of the sourced staging symbols are reachable unless `STAGING=y`.

State and persistence: configuration state is stored in kernel build `.config`, not runtime state.

Dependencies and integration: integrates staging subdirectories into the kernel configuration graph and pairs with `drivers/staging/Makefile` for build inclusion.

Risks: ordering can affect menu presentation and dependency diagnostics. Missing or renamed sourced files break configuration. Enabling staging intentionally exposes less mature drivers and can taint support status.

Test signals: run `make menuconfig`/`olddefconfig` with `STAGING=y` and `n`, verify all sourced paths exist, and check that disabling `STAGING` hides FBTFT and axis-fifo options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/Kconfig -->
