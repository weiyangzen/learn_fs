# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/HalPwrSeqCmd.h

Purpose: this header defines the compact power-sequence command format used to execute Realtek card enable, disable, and low-power flows.

Important APIs/types/macros: command values are `PWR_CMD_READ`, `PWR_CMD_WRITE`, `PWR_CMD_POLLING`, `PWR_CMD_DELAY`, and `PWR_CMD_END`. Base address constants include `PWR_BASEADDR_MAC` and `PWR_BASEADDR_SDIO`; interface masks include `PWR_INTF_SDIO_MSK`, USB, PCI, and all. `struct wlan_pwr_cfg` packs offset, cut/fab/interface masks, base, command, mask, and value. Accessor macros such as `GET_PWR_CFG_OFFSET`, `GET_PWR_CFG_CMD`, and `GET_PWR_CFG_VALUE` hide the packed fields. The main function prototype is `HalPwrSeqCmdParsing`.

Control flow and integration: `sdio_halinit.c` passes SDIO-specific flow arrays (`rtl8723B_card_enable_flow`, `rtl8723B_enter_lps_flow`, `rtl8723B_card_disable_flow`) to `HalPwrSeqCmdParsing`, with all cut/fab masks and SDIO interface mask. The parser interprets table rows, performing reads/writes/polls/delays until an END command.

State and persistence: the header stores no state; table execution changes MAC/SDIO power registers and determines whether `hal_com_data.bMacPwrCtrlOn` can be set.

Dependencies: includes `drv_types.h`, so it depends on the adapter type and broad driver includes.

Risks and test signals: bitfield layout in `struct wlan_pwr_cfg` must match table initializers and compiler ABI assumptions. Polling commands need bounded timeouts in the parser. Tests should validate card enable/disable flow success, low-power entry, interface-mask filtering, and behavior when a polling condition never becomes true.
