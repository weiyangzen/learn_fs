<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Kconfig

Purpose: Declares the `VIDEO_COBALT` kernel configuration option for the Cisco Cobalt PCIe V4L2 driver.

Important APIs/types: The symbol is a tristate module option. It depends on V4L2 device support, I2C, PCI MSI, complex MTD mappings, sound, MTD, and either a GPIOLIB/non-conflicting ADV7511 setup or compile-test. It selects media controller support, V4L2 subdevice API, I2C algorithm support, ALSA PCM, ADV7604/ADV7511/ADV7842 subdevice drivers, and vb2 DMA scatter-gather support.

Control flow: Kconfig selection determines whether `cobalt.o` is built and which framework/subdevice dependencies are enabled. At runtime the module registers a PCI driver for Cisco Cobalt devices.

State/persistence: No runtime state; it controls build-time availability and module linkage.

Dependencies/integration: The dependencies match the implementation: MSI is used for interrupts, MTD map support for NOR flash, ALSA PCM for audio nodes, ADV subdevices for HDMI input/output, and vb2 DMA-SG for buffer handling.

Risks: The `DRM_I2C_ADV7511=n` dependency avoids collision with a DRM ADV7511 driver, but can surprise users with unmet dependencies. Selecting many subdrivers increases build surface and may hide missing optional hardware until probe time.

Test signals: Kconfig allmodconfig/allyesconfig coverage, compile-test builds, module autoload, and dependency-resolution checks when ADV7511 DRM support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Kconfig -->
