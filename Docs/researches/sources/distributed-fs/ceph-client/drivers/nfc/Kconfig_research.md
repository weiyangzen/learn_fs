# sources/distributed-fs/ceph-client/drivers/nfc/Kconfig

Purpose: Defines the top-level Kconfig menu for NFC device drivers below `drivers/nfc`, gated by the core `NFC` subsystem. It exposes selectable transport/controller drivers and sources subordinate Kconfig files for driver families.

Important APIs, types, and functions: Kconfig symbols include `NFC_TRF7970A`, `NFC_MEI_PHY`, `NFC_SIM`, `NFC_PORT100`, and `NFC_VIRTUAL_NCI`, plus `source` statements for FDP, PN544, PN533, Microread, Marvell, ST, NXP, Samsung, and ST95HF subtrees.

Control flow: There is no runtime control flow. Build-time selection flows from `menu "Near Field Communication (NFC) devices"` through dependencies such as `SPI`, `USB`, `NFC_DIGITAL`, `NFC_HCI`, `NFC_NCI`, `INTEL_MEI`, and `GPIOLIB`.

State and persistence behavior: The file persists user build choices in kernel configuration. It does not create runtime state.

Dependencies and integration points: Integrates NFC driver families with the kernel Kconfig system and controls which Makefile objects can be built. `NFC_MEI_PHY` is a shared transport used by MEI-backed HCI drivers such as Microread.

Risks: Incorrect dependencies can allow build failures or hide valid drivers. Top-level source ordering matters for menus but not runtime. A transport helper like `NFC_MEI_PHY` must remain selectable only with compatible core APIs.

Test signals: Run `make menuconfig`/`olddefconfig` dependency checks, build each symbol as module and built-in where supported, and verify sub-Kconfig source paths remain valid after tree moves.
