# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/defs.h

Purpose: Provides broad shared constants for Broadcom bus types, tri-state control values, 802.1D priorities, ioctl-like command IDs, radio-disable bits, TX power override, band IDs, debug levels, power-management modes, Sonics backplane offset, and padding macro support.

Important APIs/constants: Defines `OFF`, `ON`, `AUTO`, priority values and `NUMPRIO`, `WL_NUMRATES`, country buffer size, command numbers for channel/rates/PHY list, radio disable masks, `WL_TXPWR_OVERRIDE`, `BRCM_BAND_*`, debug flags consumed by `brcm_msg_level`, PM modes, `SBCONFIGOFF`, and `PAD`.

Control flow and state: No executable flow. The `PAD` macro generates unique field names for register-layout padding, affecting struct definitions such as chipcommon.

Dependencies and integration: Includes Linux types. Consumed across brcmsmac, brcmutil, and include headers. Risks include name collisions from generic constants, command-ID compatibility, duplicated band definitions with `brcmu_wifi.h`, and accidental changes to `PAD` breaking register layout declarations. Test signals include compile coverage, debug logging flag behavior, command dispatch paths, radio disable reporting, and struct layout offset checks.
