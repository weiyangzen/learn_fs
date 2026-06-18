# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/Kconfig

Purpose: top-level Kconfig include file for Samsung media platform drivers.

Important APIs and symbols: it emits a menu comment and sources child Kconfig files for `exynos-gsc`, `exynos4-is`, `s3c-camif`, `s5p-g2d`, `s5p-jpeg`, and `s5p-mfc`.

Control flow: during kernel configuration, inclusion from the media platform Kconfig tree makes each Samsung subdriver's symbols visible. No runtime code is involved.

State and persistence: selected symbols persist only in the kernel build configuration.

Dependencies and integration points: integrates the Samsung platform media subdirectory into the broader media Kconfig hierarchy. The `exynos-gsc` source line is the entry point for `VIDEO_SAMSUNG_EXYNOS_GSC`.

Risks: adding/removing Samsung subdirectories requires keeping this source list synchronized with the Makefile. Incorrect source paths break menuconfig/allconfig processing.

Test signals: `make menuconfig`, `olddefconfig`, and allmodconfig coverage that reaches every sourced child Kconfig.
