<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Kconfig

Purpose: defines build-time configuration for the Silicon Labs Si4713 FM transmitter stack.

Important APIs and symbols: `USB_SI4713` enables the USB development-board wrapper and selects `I2C_SI4713`; `PLATFORM_SI4713` enables the platform/I2C V4L2 radio wrapper and selects `I2C_SI4713`; `I2C_SI4713` builds the core Si4713 I2C subdevice driver. All depend on `RADIO_SI4713` and I2C as appropriate, with USB support additionally depending on USB.

Control flow: selected symbols drive the Makefile: core command/control support lives in `si4713.o`, while USB and platform entry points wrap the same subdevice through different bus exposure paths.

State and persistence: no runtime state. Kconfig choices persist in the kernel build configuration and determine whether modules `si4713`, `radio-usb-si4713`, and `radio-platform-si4713` exist.

Dependencies and integration points: integrates with the media radio Kconfig tree, V4L2 radio support, I2C, USB, and the parent `RADIO_SI4713` menu symbol. The select relationships ensure wrappers get the core I2C command driver.

Risks: selecting `I2C_SI4713` from wrappers means invalid or partial module combinations are avoided, but `I2C_SI4713` remains user-selectable on its own and then provides only a subdevice unless another driver instantiates or registers it.

Test signals: `allmodconfig`/`allyesconfig` build coverage, module dependency inspection, and menuconfig visibility with and without USB/I2C/radio prerequisites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Kconfig -->
