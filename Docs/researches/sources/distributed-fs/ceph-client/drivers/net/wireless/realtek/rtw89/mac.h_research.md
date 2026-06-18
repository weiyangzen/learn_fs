# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/mac.h

## Purpose

`mac.h` is the central MAC-layer contract for the Realtek `rtw89` wireless driver. It defines register/memory layout constants, MAC-generation dispatch hooks, public MAC APIs, and inline helpers used by core, firmware, power-save, WoW, debug, and chip-specific files. The file deliberately separates common call sites from AX/BE hardware differences through `struct rtw89_mac_gen_def`, with `rtw89_mac_gen_ax` and `rtw89_mac_gen_be` supplied by implementation files.

## Important APIs, Types, And Constants

- Hardware selection and forwarding enums include `rtw89_mac_hwmod_sel`, `rtw89_mac_fwd_target`, frame type selectors, DLE/PLE port and queue IDs, quota IDs, firmware C2H classes/functions, MCC/MRC statuses, WoW firmware states, and MAC error codes.
- Memory and CAM definitions map symbolic selectors in `enum rtw89_mac_mem_sel` to AX/BE SRAM windows such as AXIDMA, shared buffer, DMAC table, address CAM, security CAM, BSSID CAM, BA CAM, beacon IE CAMs, TXD/TXDATA FIFOs, CPU local memory, WD page, and MLD table.
- `struct rtw89_mac_size_set` groups the driver's common DLE/HFC size, quota, reserved quota, and DLE input presets. The exported `rtw89_mac_size` object is used by initialization and quota-selection code outside this header.
- `struct rtw89_mac_gen_def` is the key polymorphic interface. It contains register offsets and many function pointers for system/TRX init, DLE/HFC setup, firmware download, efuse parsing, CPU IO, coex grant/PLT, TX power register mapping, scan offload, WoW MAC configuration, error dumps, and beamforming association.
- Inline register helpers, including `rtw89_mac_reg_by_idx()`, `rtw89_mac_reg_by_port()`, and the `rtw89_read/write*_port*()` wrappers, centralize band and port address translation. BE chips use `RTW89_MAC_BE_BAND_REG_OFFSET`; AX chips use their own offset from the generation definition.
- Public MAC APIs declared here cover power on/off, partial/pre/full init, DLE/HFC/preload init, VIF and port management, TSF operations, beacon/AP control, BB/RF enablement, C2H handling, scheduler stop/resume, RX filtering, coexistence, control-path switching, beamforming, MU-EDCA, TX power accessors, packet drop, DLE quota changes, reserved quota lookup, and CPU IO RX movement.
- TX report helpers (`rtw89_tx_rpt_init()`, `rtw89_is_tx_rpt_skb()`, `rtw89_tx_rpt_tx_status()`, `rtw89_tx_rpt_skb_add()`, `rtw89_tx_rpt_skbs_purge()`) bridge firmware TX completion reports back to mac80211 status reporting.

## Control Flow And Dispatch

Most common code calls a small inline wrapper in this header, which then dispatches through `rtwdev->chip->mac_def`. Examples include MAC enable checks, PPDU status, PHY reports, EDCCA mode, coexistence PLT, beamforming association, TX power CR lookup, XTAL SI access, scan offload, and secure IDMEM sharing. This lets shared files such as `mac.c`, `fw.c`, `wow.c`, `ps.c`, `ser.c`, `debug.c`, and `mac80211.c` avoid open-coded chip-generation branches.

Register flow is similarly centralized. Callers supply a base register and band or port identity; helpers derive the physical register using the generation-specific band offset and the `struct rtw89_port_reg` table. This is important for DBCC/MLO paths where the same logical operation may need CMAC0 or CMAC1 programming.

TX reporting flow is local to the header because it is performance-sensitive and small: transmit setup assigns a 4-bit firmware report sequence number from `rtwdev->tx_rpt.sn`; SKBs needing status are stored in the indexed `tx_rpt->skbs` array under `skb_lock`; a collision on the same sequence number is treated as late firmware reporting and the old SKB is completed as dropped; purge drains all pending SKBs with drop status.

## State And Persistence Behavior

This header does not own persistent storage, but it defines the state surfaces other modules mutate:

- `rtwdev->chip->mac_def` chooses AX or BE behavior for the lifetime of the device.
- `rtwdev->hal.rx_fltr`, `rtwdev->dbcc_en`, `rtwdev->hci`, `rtwdev->mac.hfc_param`, `rtwdev->mac.dle_info`, and `rtwdev->mac.qta_mode` are read or indirectly modified through declared APIs and generation callbacks.
- Device flags such as `RTW89_FLAG_BFEE_MON`, power/function flags, SER handling, and firmware-ready state gate helper behavior.
- `rtwdev->tx_rpt` persists outstanding TX-status SKB pointers until firmware completion, collision replacement, or purge.
- Hardware state is persistent in MMIO registers, CAMs, DLE quota tables, and firmware-owned tables; this header's API boundaries are the common entry points for configuring those resources.

## Dependencies And Integration Points

`mac.h` includes `core.h`, `fw.h`, and `reg.h`, so it depends on core device/vif/sta data structures, firmware command types, and register definitions. It exposes symbols consumed by `mac.c`, `mac_be.c`, `mac80211.c`, chip files such as `rtw8922a.c` and `rtw8922d.c`, and support modules including firmware, WoW, SER, power save, debugfs, PHY, coexistence, and CAM/security code. It also integrates directly with mac80211 through SKB control blocks and `ieee80211_tx_status_irqsafe()` in TX report helpers.

## Risks And Edge Cases

- `struct rtw89_mac_gen_def` is a wide vtable; missing optional callbacks must be checked before use. Some wrappers guard NULL callbacks, while others assume the chip definition is complete.
- Register offset helpers are correctness-critical. A wrong band offset, port index, or generation-specific register base can silently program the wrong CMAC.
- `rtw89_mac_mem_base_addrs()` special-cases RTL8922D security CAM; adding new memory selectors or chip variants requires keeping this mapping synchronized with `enum rtw89_mac_mem_sel`.
- TX report sequence numbers are only 4 bits. The collision handling avoids leaks but can report older SKBs as dropped when firmware reports are delayed or queue pressure is high.
- `rtw89_mac_chk_preload_allow()` currently always returns false after the HCI/chip check comment, so any future preload enablement must be intentional and retested for BE/PCIe devices.
- Inline helpers touch MMIO and mac80211 status paths; they must only be called under the locking and power-state assumptions documented by their callers.

## Test Signals

- Build coverage should include AX and BE chip files because this header's vtable shape must match all generation definitions.
- Runtime smoke tests should cover interface add/remove, STA association/disassociation, scan offload, WoW suspend/resume, DBCC/MLO link activation, and TX-status reporting.
- Debug and fault-injection signals include SER recovery, DLE quota lost dumps, TX report purge/collision behavior, PPDU status enable/disable, and RX filter changes across CMAC0/CMAC1.
- Static checks should flag missing generation callbacks, enum/table size mismatches, and unsafe NULL callback assumptions.
