# sources/distributed-fs/ceph-client/drivers/net/can/usb/Kconfig

Purpose: Declares Kconfig options for USB-attached CAN interface drivers under `drivers/net/can/usb`.

Important APIs, types, and functions: Declarative Kconfig menu depending on USB. Defines tristate symbols for 8devices, EMS, esd, ETAS ES58X, Fintek F81604, GS/candleLight, Kvaser, Microchip CAN BUS Analyzer, Nuvoton NCT6694, PEAK, and Theobroma UCAN drivers. Some entries select `CRC16`, `NET_DEVLINK`, or `CAN_RX_OFFLOAD`, and NCT6694 depends on `MFD_NCT6694`.

Control flow: Kernel configuration choices drive compilation in the sibling Makefile. Help text documents supported hardware and module names.

State and persistence behavior: Choices persist in `.config`; tristate values determine built-in, module, or disabled build products.

Dependencies and integration points: Integrates with the CAN/USB build system and driver subdirectories. Menu-level USB dependency hides these drivers without USB support.

Risks: Missing dependency declarations can cause build or runtime failures. Help text/module names can drift from Makefile outputs.

Test signals: `menuconfig`/`olddefconfig` with USB on/off, each option as `m` and `y`, selected dependency checks, and generated module name comparisons.
