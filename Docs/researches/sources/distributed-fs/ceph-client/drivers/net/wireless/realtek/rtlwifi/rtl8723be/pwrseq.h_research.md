<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.h

## Purpose
Defines the RTL8723B power transition scripts consumed by the rtlwifi power-sequence executor. The file maps high-level NIC transitions such as power on, radio off, suspend, resume, hardware power down, and LPS enter/leave into ordered `struct wlan_pwr_cfg` register commands.

## Important APIs, Types, And Functions
- Includes `../pwrseqcmd.h` for `struct wlan_pwr_cfg`, command IDs, base-address selectors, cut/fab/interface masks, and delay constants.
- Step-count macros include `RTL8723B_TRANS_CARDEMU_TO_ACT_STEPS`, `RTL8723B_TRANS_ACT_TO_CARDEMU_STEPS`, `RTL8723B_TRANS_CARDEMU_TO_SUS_STEPS`, `RTL8723B_TRANS_CARDEMU_TO_PDN_STEPS`, `RTL8723B_TRANS_ACT_TO_LPS_STEPS`, `RTL8723B_TRANS_LPS_TO_ACT_STEPS`, and `RTL8723B_TRANS_END_STEPS`.
- Command-list macros include `RTL8723B_TRANS_CARDEMU_TO_ACT`, `RTL8723B_TRANS_ACT_TO_CARDEMU`, `RTL8723B_TRANS_CARDEMU_TO_SUS`, `RTL8723B_TRANS_SUS_TO_CARDEMU`, card-disable/card-enable aliases, `RTL8723B_TRANS_CARDEMU_TO_PDN`, `RTL8723B_TRANS_PDN_TO_CARDEMU`, `RTL8723B_TRANS_ACT_TO_LPS`, `RTL8723B_TRANS_LPS_TO_ACT`, and `RTL8723B_TRANS_END`.
- Extern flow arrays include `rtl8723B_power_on_flow`, `rtl8723B_radio_off_flow`, `rtl8723B_card_disable_flow`, `rtl8723B_card_enable_flow`, `rtl8723B_suspend_flow`, `rtl8723B_resume_flow`, `rtl8723B_hwpdn_flow`, `rtl8723B_enter_lps_flow`, and `rtl8723B_leave_lps_flow`.
- Public aliases such as `RTL8723_NIC_PWR_ON_FLOW`, `RTL8723_NIC_RF_OFF_FLOW`, `RTL8723_NIC_DISABLE_FLOW`, and `RTL8723_NIC_LPS_LEAVE_FLOW` provide chip-family names to the rest of the driver.

## Control Flow
This header has no executable functions. The control flow is the array order itself: each entry selects a register offset, hardware cut/fab/interface applicability, base address, command type, bit mask, and value. The power-sequence runner executes writes, polls, delays, and `PWR_CMD_END` in order. The active path releases isolation, disables suspend and HWPDN bits, polls power-ready and MAC-off bits, restores WLON reset, and configures GPIO9 wake interrupt wiring. The low-power entry path stops PCIe DMA, pauses transmit, polls transmit queues empty, gates BB/OFDM/CCK clocks, resets MAC TRX, and responds TxOK to the scheduler. The low-power exit path writes RPWM for SDIO/USB/PCIe, waits, restores TSF/BB/MAC clocks, and unpauses transmit.

## State And Persistence
The state is persisted in device registers and power islands, not in kernel memory. Key state includes MAC isolation, LDO and crystal ownership, WL suspend/HWPDN bits, WLON reset, PCIe DMA stop/start, transmit pause, baseband reset, GPIO wake interrupt enables, and SDIO local suspend state. The exported flow arrays are defined in the companion `pwrseq.c` and remain static kernel data for all devices using the module.

## Dependencies And Integration Points
The file depends on rtlwifi's generic power-sequence interpreter and is integrated by the RTL8723BE hardware init, suspend/resume, disable, and low-power code. The same macro set contains USB, SDIO, and PCIe masks even though this PCI driver primarily uses the PCIe entries. Register offsets correspond to RTL8723B MAC, SDIO local, and power-management registers defined elsewhere.

## Risks And Edge Cases
Step-count macros must match the macro bodies used by `pwrseq.c`; mismatches can overrun or truncate flow arrays. Polling commands can hang if firmware or hardware state machines do not reach the expected bit values. Interface masks are easy to regress because USB/SDIO/PCIe commands are mixed in the same sequence. Incorrect power ordering can leave RF on during disable, lose wake events, or break resume from LPS/suspend.

## Test Signals
Useful signals are successful probe power-on, RF on/off toggles, suspend/resume, runtime LPS entry/exit under traffic, no stuck polling during module load/unload, valid wake interrupt behavior on GPIO9, and no transmit queue stall after leaving LPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.h -->
