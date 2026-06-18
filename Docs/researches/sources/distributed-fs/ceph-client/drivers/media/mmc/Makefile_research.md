# sources/distributed-fs/ceph-client/drivers/media/mmc/Makefile

Purpose: top-level Kbuild file for MMC/SDIO media drivers.

Important APIs/types/functions: `obj-y += siano/` always descends into the Siano subdirectory; subdirectory Kbuild decides whether concrete objects are built.

Control flow: Kbuild visits `drivers/media/mmc/siano` whenever this directory is part of the build.

State/persistence: build-only state; no runtime behavior.

Dependencies/integration: integrates with Kbuild and the Siano media SDIO driver Makefile.

Risks/test signals: unconditional descent is safe if the subdir gates objects correctly. Build tests should cover `SMS_SDIO_DRV=n/m/y` to ensure no unwanted object is linked.
