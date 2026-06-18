# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hdr.h

## Purpose
This header defines low-level register maps, bit constants, address windows, device states, firmware error helpers, interrupt register mappings, NIU flow-control helpers, mailbox CRB addresses, memory address ranges, and small hardware mapping structs for qlcnic 82xx/P3P-style hardware. It is a foundational hardware ABI header used by init, ethtool, context, interrupt, flash, and link-management code.

## Important APIs, Types, And Definitions
- Hub/agent enumerations define CRB hub addresses and PX map indices for PH/PS/MN/MS/PEG/SRE/NIU/QM/SQ/CAS/I2C/ROMUSB and related blocks.
- `BIT_0` through `BIT_31`, `LSB/MSB/LSW/MSW/LSD/MSD`, and many register-address macros support compact hardware bitfield programming.
- CRB windows: `QLCNIC_PCI_CRB_WINDOW*`, `QLCNIC_CRB_*`, PEG, DDR/QDR/OCM ranges, ROMUSB, CAM, NIU, timer, I2Q, and PCI host/MD windows.
- Mailbox command register macros: `QLCNIC_CDRP_ARG()`, `QLCNIC_CDRP_CRB_OFFSET`, and `QLCNIC_SIGN_CRB_OFFSET`.
- Link/port helpers: `XG_LINK_STATE_P3P()`, `P3P_LINK_SPEED_REG()`, `P3P_LINK_SPEED_VAL()`, `QLCNIC_PORT_MODE_*`, and NIU pause/flow-control bit setters/getters.
- Device state and function mode enums include cold/initializing/ready/need-reset/failed/quiescent states and management/privileged/non-privileged/SR-IOV modes.
- Firmware error macros parse fatal/error code fields and define fan failure.
- Interrupt definitions include legacy target status/mask registers for functions 0-7 and `QLCNIC_LEGACY_INTR_CONFIG`.
- Structs `qlcnic_legacy_intr_set`, `crb_128M_2M_sub_block_map`, and `crb_128M_2M_block_map` describe interrupt register sets and CRB address translation maps.

## Control Flow
The header has no executable control flow, but its macros determine how source files compute hardware addresses and manipulate state. Context code writes mailbox arguments through `QLCNIC_CDRP_ARG()`. Ethtool reads link, pause, WOL, and diagnostic registers defined here. Init and reset code compares device states, heartbeat timing constants, and firmware error codes. Interrupt setup uses the legacy interrupt config initializer.

## State And Persistence Behavior
Definitions in this header map directly to persistent hardware state: CRB registers, CAM RAM, ROM/flash windows, shared device-state registers, WOL config, link speed/state, pause masks, firmware heartbeat/PEG halt registers, mailbox registers, and interrupt masks/status. Writes through these macros can persist in device registers across driver operations and sometimes across function resets depending on hardware block.

## Dependencies And Integration Points
The header includes Linux kernel types and `qlcnic_hw.h`. It is consumed by most qlcnic low-level C files, especially ethtool, context/mailbox, hardware register access, reset, link, and flash code. It bridges driver logic to firmware/hardware ABI constants; changing values without matching hardware documentation would affect many paths.

## Risks And Edge Cases
- Macros with side effects such as `qlcnic_gb_rx_flowctl(config_word)` modify their argument expression; callers must pass mutable lvalues.
- Many numeric constants are hardware ABI values with no type safety; a wrong register base or bit shift can silently access the wrong device block.
- Duplicated comments around NIU XG pause control and dense hub-agent mapping make maintenance error-prone.
- Legacy BIT macros may conflict conceptually with kernel `BIT()` usage, but local code expects these exact constants.
- Device-state constants here are distinct from 83xx IDC state constants in other headers; mixing state domains would cause invalid transitions.

## Test Signals
Validation signals include successful mailbox commands using CDRP offsets, correct ethtool register/link/pause/WOL behavior, interrupt delivery for legacy/MSI-X paths, flash/ROMUSB access, heartbeat and PEG halt diagnostics, and regression tests or hardware smoke tests after any register macro changes.
