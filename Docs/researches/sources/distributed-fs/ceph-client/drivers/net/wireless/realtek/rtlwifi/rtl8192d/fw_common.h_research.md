# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/fw_common.h

Purpose: Defines RTL8192D firmware layout constants, firmware-header accessors, rate-mask H2C packing, and shared firmware function prototypes.

Important APIs/types: `FW_8192D_START_ADDRESS`, page size, and polling timeout describe firmware transfer. `IS_FW_HEADER_EXIST()` recognizes supported firmware signatures. Header macros decode little-endian signature/version/subversion fields. `struct rtl92d_rate_mask_h2c` packs the 32-bit rate mask/RAID word and MACID/short-GI byte used by rate adaptation commands.

Control flow: Header macros are used by rtl8192de firmware download before stripping a 32-byte header, and by hardware rate-mask updates before calling `rtl92d_fill_h2c_cmd(H2C_RA_MASK, ...)`.

State and persistence: No storage; it defines the binary layout of firmware headers and H2C payloads. Packing and endian annotations are important because payload bytes are written directly to firmware mailboxes.

Dependencies and integration: Requires kernel bitfield helpers, `enum version_8192d`, `struct rtl_priv`, and `struct ieee80211_hw` from surrounding rtlwifi headers. Used by common firmware code, rtl8192de firmware code, and common hardware rate-control code.

Risks: Header signature checks include 8192C/8188C-compatible values as well as 8192D values; tightening this could reject accepted firmware. Any struct layout or mask change changes firmware ABI.

Test signals: Build-time type/layout checks, firmware version logging, successful `H2C_RA_MASK` commands, and association throughput across 11b/g/n rates.
