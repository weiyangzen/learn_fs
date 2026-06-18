# sources/distributed-fs/ceph-client/sound/soc/sdca/Kconfig

## Purpose
Kconfig menu for the SoundWire Device Class for Audio support. It defines the common SDCA library, optional HID/IRQ/FDL features, the class-compliant SoundWire driver, and auxiliary function driver support.

## APIs, Types, and Functions
Defines `SND_SOC_SDCA`, `SND_SOC_SDCA_HID`, `SND_SOC_SDCA_IRQ`, `SND_SOC_SDCA_FDL`, `SND_SOC_SDCA_OPTIONAL`, `SND_SOC_SDCA_CLASS`, and `SND_SOC_SDCA_CLASS_FUNCTION`. `SND_SOC_SDCA_CLASS` selects function, FDL, HID, IRQ, and SoundWire regmap support; `SND_SOC_SDCA_CLASS_FUNCTION` selects MBQ SoundWire regmap support.

## Control Flow, State, and Persistence
This file has no runtime state. Its control effect is build-time dependency wiring: SDCA requires ACPI for the base library, class support requires SOUNDWIRE and compatible HID settings, and optional subfeatures are default-enabled when the base is enabled.

## Dependencies and Integration
Integrates the SDCA source directory with ACPI, HID, AUXILIARY_BUS, SOUNDWIRE, REGMAP, REGMAP_IRQ, REGMAP_SOUNDWIRE, and REGMAP_SOUNDWIRE_MBQ subsystems. It also ensures the class driver can publish auxiliary function devices and consume the shared library.

## Risks and Test Signals
Risks include dependency combinations where HID is modular or built-in differently from SDCA, optional features being default-on and increasing build surface, and class driver builds requiring selected lower-level regmap features. Test signals are `allyesconfig`, `allmodconfig`, SDCA without class driver, class driver as module, and configurations with HID disabled or built in.
