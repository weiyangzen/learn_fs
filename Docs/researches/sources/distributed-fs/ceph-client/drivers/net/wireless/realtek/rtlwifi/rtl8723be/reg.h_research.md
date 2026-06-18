<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/reg.h

## Purpose
Provides the RTL8723BE register map, bit masks, descriptor/control constants, baseband register aliases, RF register masks, EFUSE definitions, interrupt masks, and wake-on-WLAN flags used across the chip-specific driver. It is the central symbolic contract between driver code and RTL8723BE hardware registers.

## Important APIs, Types, And Functions
- System and power registers: `REG_SYS_ISO_CTRL`, `REG_SYS_FUNC_EN`, `REG_APS_FSMCO`, `REG_SYS_CLKR`, `REG_RSV_CTRL`, `REG_RF_CTRL`, LDO/AFE/PLL controls, EFUSE registers, GPIO and LED configuration registers.
- MAC/queue registers: command/control registers, DMA queues, beacon/TBTT/TSF controls, EDCA parameters, retry limits, NAV controls, response rate sets, security CAM registers, and packet buffer selectors.
- Interrupt definitions: normal IMR/HISR bits such as `IMR_ROK`, `IMR_RDU`, `IMR_BEDOK`, `IMR_C2HCMD`, `IMR_HSISR_IND_ON_INT`, plus high-speed/system interrupt bits.
- Baseband aliases: `RFPGA0_*`, `ROFDM0_*`, `RCCK0_*`, AGC, IQ imbalance, CCK/OFDM counters, TXAGC registers such as `RTXAGC_A_RATE18_06`, and RF serial-interface masks such as `BLSSIREADADDRESS`.
- Generic masks and helpers: `MASKBYTE0`, `MASKBYTE1`, `MASKDWORD`, `RFREG_OFFSET_MASK`, `BIT`-based control fields, antenna constants, WOWLAN event and reason bits, and `EFUSE_SEL` helpers.

## Control Flow
There is no runtime control flow. Other files use these macros to perform register reads and writes through `rtl_read_*`, `rtl_write_*`, `rtl_get_bbreg`, `rtl_set_bbreg`, RF serial helpers, descriptor helpers, interrupt recognition, firmware download, and power sequencing. The header enables common code to express register operations symbolically instead of embedding numeric offsets in each path.

## State And Persistence
All constants address persistent hardware state. They cover power domains, firmware/8051 state, PCIe DMA engines, packet buffers, EFUSE contents, security CAM entries, TSF/beacon timers, dynamic management counters, BB/RF calibration state, and wake-on-WLAN status. The header itself persists no state.

## Dependencies And Integration Points
Included by RTL8723BE hardware, PHY, RF, firmware, TX/RX, software registration, and dynamic-management files. It also aligns with shared rtlwifi core abstractions that use `rtl_hal_cfg.maps[]` to translate generic rtlwifi register roles into chip-specific offsets. The definitions must match the vendor datasheet and the initialization arrays in `table.c`.

## Risks And Edge Cases
Wrong offsets or masks can silently corrupt unrelated hardware fields. Many masks are reused with partial-register operations, so width and shift mistakes can cause power, DMA, interrupt, RF, or security regressions. The file also contains broad legacy compatibility definitions; deleting apparently unused symbols can break chip-family shared code. WOWLAN and EFUSE definitions are especially sensitive because invalid values can persist across suspend or device reinitialization.

## Test Signals
Validation comes from successful module load, firmware download, interrupt recognition, TX/RX traffic, beacon operation in AP/IBSS modes, suspend/resume, RF calibration, EFUSE parsing, security offload, and wake-on-WLAN event handling. Static signals include compile coverage of every including file and sparse/build warnings for invalid masks or duplicate definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/reg.h -->
