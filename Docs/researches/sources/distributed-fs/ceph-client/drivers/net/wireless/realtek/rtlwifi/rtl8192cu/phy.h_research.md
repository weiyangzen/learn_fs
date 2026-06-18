
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/phy.h

Purpose: Declares CU PHY entry points while importing the CE PHY header for shared RTL8192C definitions.

Important APIs/functions: Exposes BB enable, RF path legality, IO command, MAC/BB/RF table configuration, RF register query/set, LC calibration, bandwidth callback, and RF power-state functions. It includes `../rtl8192ce/phy.h`, so many common 8192C PHY constants and prototypes are inherited.

Control flow: Header only. These prototypes are consumed by `hw.c`, `rf.c`, and `sw.c` HAL operation setup.

State and persistence: Exposed functions manipulate `rtl_phy`, RF/BB registers, channel bandwidth state, power state, and table-derived calibration data.

Dependencies/integration: Bridges CU code to common/CE PHY infrastructure. `rtl8192_phy_check_is_legal_rfpath()` is implemented in common 8192C PHY code and exported there.

Risks: Because this header layers on CE PHY declarations, incompatible CE changes can affect CU. Duplicate declarations of common functions must remain ABI-compatible. Any new PHY callback added to `rtl_hal_ops` needs a matching declaration here or in included common headers.

Test signals: Compile with `CONFIG_RTL8192CU`, static symbol resolution for common PHY exports, and runtime exercise of each HAL PHY callback.
