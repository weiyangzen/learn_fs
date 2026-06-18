## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/Kconfig

Purpose: Kconfig entry for the ASPEED AST PCI server graphics DRM/KMS driver.

Important symbol is `DRM_AST`, a tristate depending on DRM and PCI. It selects DRM client setup, shmem GEM helpers, KMS helpers, I2C, and I2C bit-banging support. Help text warns that the driver is experimental and intended for server chipsets with modesetting support.

Control flow is build-time only. State is kernel configuration and module enablement. Runtime dependencies implied by the selection include PCI BAR access, DRM shmem framebuffer allocation, I2C/DDC for VGA EDID, and KMS helper infrastructure.

Risks are stale help wording relative to the modern atomic driver and broad PCI matching that depends on runtime chip detection. Test signals are config dependency resolution, compile-test coverage where possible, `ast` module build, and successful loading on supported ASPEED PCI display devices.
