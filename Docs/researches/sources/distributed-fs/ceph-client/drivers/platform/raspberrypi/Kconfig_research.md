# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/Kconfig

Purpose: Kconfig menu for Broadcom VideoCore support on Raspberry Pi platforms, including the VCHIQ core and optional userspace character device, plus the MMAL-over-VCHIQ service.

Important APIs, types, and functions: `menuconfig BCM_VIDEOCORE` gates the subsystem and depends on OF plus Raspberry Pi firmware support or compatible compile-test conditions. `config BCM2835_VCHIQ` enables the VCHIQ messaging driver and depends on `HAS_DMA`; it implies `VCHIQ_CDEV`. `config VCHIQ_CDEV` controls `/dev/vchiq` ioctl exposure. The file sources `drivers/platform/raspberrypi/vchiq-mmal/Kconfig`.

Control flow: Kconfig determines whether the VCHIQ platform driver, bus, debugfs, optional cdev, and MMAL child directory are built.

State and persistence: configuration state is persisted in `.config`; no runtime state.

Dependencies and integration points: integrates Raspberry Pi firmware mailbox support, device tree, DMA-capable builds, kernel consumers such as audio/camera/MMAL, and optional userspace ABI exposure.

Risks: `BCM_VIDEOCORE` defaults to `y`, but buildability depends on firmware availability or compile-test path. Disabling `VCHIQ_CDEV` removes userspace ABI while preserving kernel-client support; downstream userland libraries may assume it exists.

Test signals: generate configs for Raspberry Pi firmware-enabled builds, compile-test builds without firmware, VCHIQ as module/built-in, and `VCHIQ_CDEV=n`; verify object selection and user-facing device presence match expectations.
