# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/regs.h

## Purpose
`regs.h` is the register map and bit-field vocabulary for the `rtl8xxxu` USB Realtek driver. It names the hardware address space used by chip initialization, firmware download, EFUSE access, DMA setup, MAC/WMAC programming, security CAM access, beacon timing, RF/BB calibration, USB SIE configuration, and 8710B indirect/SYSON access. The file has no executable code; its value is the stable contract between chip-specific driver routines and Realtek RTL8xxxU-family hardware.

## Important APIs, Types, And Functions
The file exposes preprocessor constants only. Major regions are system configuration registers `REG_SYS_ISO_CTRL` through `REG_SYS_CFG2`, MAC-top registers such as `REG_CR`, `REG_MSR`, `REG_TRXDMA_CTRL`, `REG_RQPN`, `REG_RXDMA_AGG_PG_TH`, protocol/EDCA registers such as `REG_RESPONSE_RATE_SET`, `REG_ARFR*`, `REG_EDCA_*`, beacon/TSF registers, WMAC receive/filter/security registers `REG_RCR`, `REG_RXFLTMAP*`, `REG_CAM_CMD`, `REG_SECURITY_CFG`, baseband/RF registers under `REG_FPGA*`, `REG_CCK*`, `REG_OFDM*`, TX power/IQK registers, USB endpoint/register constants under `0xfe00`, and RF6052 register identifiers.

Important bit masks encode power isolation and clocks (`SYS_ISO_*`, `SYS_FUNC_*`, `APS_FSMCO_*`, `SYS_CLK_*`), firmware load state (`MCU_FW_DL_*`), chip/vendor/package discovery (`SYS_CFG_*`, `GPIO_OUTSTS_*`), interrupt status/masks (`IMR0_*`, `IMR1_*`, `USB_HIMR_*`), TX/RX DMA queues and page loading (`TRXDMA_*`, `RQPN_*`, `RXDMA_*`), response rates (`RSR_*`), receive acceptance policy (`RCR_*`), beacon control (`BEACON_*`, `DUAL_TSF_*`), security CAM commands (`CAM_CMD_*`, `CAM_WRITE_VALID`, `SEC_CFG_*`), and 8710B normal/EFUSE indirect offsets.

## Control Flow
There is no local control flow. Runtime control flow emerges when `rtl8xxxu` implementation files call `rtl8xxxu_read8/16/32()`, `rtl8xxxu_write8/16/32()`, masked writes, RF register helpers, firmware loaders, and chip-specific init functions with these constants. Typical sequences are power-on and clock enabling via the system registers, firmware download through `REG_MCU_FW_DL` and mailbox registers, LLT/TX page programming through DMA registers, RCR/filter setup for receive paths, CAM programming for keys, and RF/BB calibration through the baseband/RF register names.

## State And Persistence
The header itself persists no state. The constants address hardware state that persists in device registers while powered and is lost across USB disconnect, firmware reset, full power-down, or suspend paths that reset the MAC/BB/RF blocks. Some registers describe one-time or semi-persistent data sources, especially EFUSE and USB SIE fields, while most are live operational state. Backup/restore users in `rtl8xxxu.h` rely on these addresses to save ADDA, MAC, and BB calibration state around IQK and channel operations.

## Dependencies And Integration Points
The definitions depend on Linux `BIT()` and `GENMASK()` style bit helpers via including translation units. They integrate with all chip-specific `rtl8xxxu` code, firmware H2C/C2H mailbox flows, USB endpoint configuration, EFUSE parsing, mac80211 channel/rate/filter state, LED classdev code, security CAM programming, and Bluetooth coexistence hooks on combo chips. Several aliases and comments document generation-specific differences for 8188E/F, 8192C/E/F, 8723A/B/U, 8812/8821, and 8710B.

## Risks
The main risk is silent hardware misprogramming: many addresses are reused with generation-specific meanings, and several masks intentionally alias bits differently on different chips. A wrong constant can disable clocks, corrupt EFUSE access, misroute USB endpoints, break beacon timing, or install keys in the wrong CAM slot. The 8710B offset/indirect access rules are especially easy to violate because low register addresses need remapping or SYSON helper access. Bit-field comments are sparse in places and inherited from vendor drivers, so changes need hardware validation rather than compile-only confidence.

## Test Signals
Useful signals include successful probe across supported USB IDs, correct chip/vendor detection from `REG_SYS_CFG`, clean firmware download and `MCU_*_READY` transitions, working RX/TX DMA without queue stalls, correct beaconing and TSF behavior in AP mode, CAM key install/remove with encrypted traffic, RF calibration and channel changes without hangs, USB interrupt/bulk endpoint behavior, and suspend/resume or reset cycles. Register-read/write debug output and hardware traces are the primary diagnostics because this file has no unit-testable logic.
