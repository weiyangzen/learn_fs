
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/def.h

Purpose: Extends/reuses RTL8192CE definitions for the USB 8192CU/8188CU variant. It imports `../rtl8192ce/def.h` and overlays chip-version bits and helpers specific to 8192CU chip identification.

Important APIs/types/functions: Defines `NORMAL_CHIP`, `CHIP_VENDOR_UMC`, `CHIP_VENDOR_UMC_B_CUT`, `IS_92C_1T2R(version)`, `IS_VENDOR_UMC(version)`, `CHIP_BONDING_92C_1T2R`, and `CHIP_BONDING_IDENTIFIER(_value)`. These are used by `mac.c`, `hw.c`, and `sw.c` to decode `REG_SYS_CFG`/`REG_HPON_FSM`, choose RF path counts, choose firmware variants, and select high-power/board behaviors.

Control flow: No runtime flow, but the macros drive branch decisions during chip-version reading, firmware selection, EEPROM parsing, RF table selection, and special UMC cut workarounds.

State and persistence: Encodes version bits stored in `rtlhal->version`. Those bits persist in driver state after probe and are used throughout the device lifetime.

Dependencies/integration: Depends on the CE definition header for base enum values such as `CHIP_92C_1T2R` and version constants. It is a compatibility layer between CU code and the shared 8192C/CE family definitions.

Risks: Bit definitions differ from 8192D and some other Realtek families. Accidentally mixing `def.h` versions can mis-detect RF type or vendor cut, leading to wrong firmware, wrong RF table, or unsafe tx-power programming.

Test signals: Probe logs should identify expected chip version and RF type for 8188CU 1T1R, 8192CU 2T2R, and UMC A/B cut devices. Firmware filename selection should match those decoded bits.
