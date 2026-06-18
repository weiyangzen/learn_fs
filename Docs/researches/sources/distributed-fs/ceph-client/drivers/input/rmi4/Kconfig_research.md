<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/Kconfig

## Purpose
`drivers/input/rmi4/Kconfig` defines build-time configuration for the Synaptics RMI4 bus, transports, and function drivers.

## Important APIs, Types, and Functions
Key symbols include `RMI4_CORE`, `RMI4_I2C`, `RMI4_SPI`, `RMI4_SMB`, `RMI4_F03`, `RMI4_F03_SERIO`, `RMI4_2D_SENSOR`, `RMI4_F11`, `RMI4_F12`, `RMI4_F1A`, `RMI4_F21`, `RMI4_F30`, `RMI4_F34`, `RMI4_F3A`, `RMI4_F54`, and `RMI4_F55`. `RMI4_CORE` selects `IRQ_DOMAIN`, `RMI4_F34` selects `FW_LOADER`, and `RMI4_F54` selects `VIDEOBUF2_VMALLOC` and `RMI4_F55`.

## Control Flow
The file is declarative. Enabling `RMI4_CORE` gates all other RMI options. Transport symbols select bus-specific modules, while function symbols include optional handlers into `rmi_core` through the Makefile.

## State and Persistence
Kconfig state persists in the kernel build configuration. It determines which code paths and symbols exist at compile time.

## Dependencies and Integration Points
The options map directly to `rmi4/Makefile`. `RMI4_SMB` is relevant to Synaptics PS/2 InterTouch fallback in `synaptics.c`; F11/F12 select the common 2D sensor helper; F03 plus F03_SERIO enables PS/2 guest/TrackPoint support.

## Risks and Edge Cases
Feature combinations can affect runtime capability: Synaptics InterTouch needs both `MOUSE_PS2_SYNAPTICS_SMBUS` and `RMI4_SMB`, while ForcePad support needs function coverage beyond a basic PS/2 path. `RMI4_F54` has a specific built-in/module dependency with `VIDEO_DEV`, so invalid configurations are blocked.

## Test Signals
Build matrix tests should cover core-only, each transport, F11/F12 2D sensor inclusion, SMBus InterTouch, F34 firmware sysfs, and module versus built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/Kconfig -->
