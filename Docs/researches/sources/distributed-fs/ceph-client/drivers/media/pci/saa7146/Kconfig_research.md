# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/Kconfig

Purpose: declares the selectable SAA7146-based board drivers for Hexium Gemini, Hexium Orion/HV-PCI6, and Siemens-Nixdorf MXB in the kernel media PCI configuration menu.

Important APIs, types, and functions: this is Kconfig metadata rather than C code. `VIDEO_HEXIUM_GEMINI`, `VIDEO_HEXIUM_ORION`, and `VIDEO_MXB` are tristate symbols. All depend on `PCI`, `VIDEO_DEV`, and `I2C`, and all select `VIDEO_SAA7146_VV`. MXB additionally selects tuner and board-specific I2C subdrivers (`VIDEO_TUNER`, `VIDEO_SAA711X`, `VIDEO_TDA9840`, `VIDEO_TEA6415C`, `VIDEO_TEA6420`) when media subdriver autoselection is enabled.

Control flow: configuration choice controls which object files the adjacent Makefile builds and which runtime module can register a `saa7146_extension`. There is no runtime flow here.

State and persistence: Kconfig selections persist in the kernel `.config`; no runtime state is stored. The tristate value determines built-in, module, or excluded behavior.

Dependencies and integration points: integrates with the media subsystem Kconfig tree and the shared `VIDEO_SAA7146_VV` core. The select statements are important because the C drivers call V4L2/SAA7146 helper APIs and, for MXB, instantiate specific I2C subdevices by name.

Risks: underselecting a dependency can produce link failures or runtime missing-subdevice behavior. Overselecting legacy drivers can increase build surface. MXB uses conditional subdriver autoselect, so manual configurations must still include the needed subdevice modules.

Test signals: `make menuconfig` visibility, `make olddefconfig` dependency resolution, module builds for `hexium_gemini`, `hexium_orion`, and `mxb`, and modprobe behavior with the expected helper modules available.
