
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/hw.h

Purpose: Declares RTL8192CU hardware constants and HAL entry points for init, security, register access, beacon control, rate updates, firmware commands, and radio checks.

Important APIs/types/functions: Defines LLT/page allocation constants such as `TX_TOTAL_PAGE_NUMBER`, `TX_PAGE_BOUNDARY`, chip A/B and WMM queue page sizes, board type masks, `enum _BOARD_TYPE_8192CUSB`, `IS_HIGHT_PA(boardtype)`, and `RTL92C_DRIVER_INFO_SIZE`. Prototypes include `rtl92cu_read_eeprom_info()`, `rtl92cu_hw_init()`, `rtl92cu_card_disable()`, `rtl92cu_set_hw_reg()`, `rtl92cu_get_hw_reg()`, `rtl92cu_update_channel_access_setting()`, `rtl92cu_gpio_radio_on_off_checking()`, firmware H2C wrappers, and `rtl92cu_update_hal_rate_tbl()`.

Control flow: Header only, but constants shape `hw.c` init logic for queue page reservation, high-power table selection, and board behavior.

State and persistence: Constants define persistent hardware packet-buffer partitioning and board-type interpretation. Function prototypes operate on `rtl_priv`, `rtl_hal`, `rtl_phy`, `rtl_usb`, `rtl_efuse`, and `rtl_ps_ctl` state.

Dependencies/integration: Included by `hw.c` and `sw.c`; it also exposes shared firmware functions from rtl8192c common code used by CU HAL ops. It ties Kbuild-visible CU code to common rtlwifi hardware variable enums.

Risks: Page-number constants must match firmware and endpoint mapping. `IS_HIGHT_PA` spelling is nonstandard but used as API; renaming can break callers. Board-type masks are used directly against EEPROM fields, so changes must be validated on real hardware variants.

Test signals: Compile coverage for all prototypes, endpoint-count/page-reservation hardware tests for one/two/three OUT endpoints, and high-power board detection checks through EEPROM fixtures.
