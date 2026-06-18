# sources/distributed-fs/ceph-client/drivers/media/mmc/siano/Makefile

Purpose: Kbuild file for the Siano SDIO transport driver.

Important APIs/types/functions: `obj-$(CONFIG_SMS_SDIO_DRV) += smssdio.o` builds the transport. `ccflags-y += -I $(srctree)/drivers/media/common/siano` gives access to shared Siano headers.

Control flow: when `SMS_SDIO_DRV` is enabled as built-in or module, `smssdio.o` is compiled with the common Siano include path.

State/persistence: build-only state.

Dependencies/integration: depends on shared common Siano source/header layout and the Kconfig-selected `SMS_SIANO_MDTV` common implementation.

Risks/test signals: include path drift breaks compilation. Build tests should cover module and built-in SDIO driver builds and ensure common Siano headers remain reachable.
