# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/def.h

Purpose: Centralizes RTL8192EE descriptor, channel-offset, queue selector, chip version, and rate-code constants.

Important APIs/types: Defines `RX_DESC_NUM_92E`, primary channel offset constants, `RX_MPDU_QUEUE`, rate classification macros, `enum version_8192e`, `enum rtl_desc_qsel`, and CCK/OFDM/HT `enum rtl_desc92c_rate` values through MCS15.

Control flow/integration: TX/RX, firmware, dynamic management, and hardware setup use these constants. `fw.c` uses the chip version enum; `dm.c` uses rate constants for adaptive fallback.

State and persistence: Stateless declarations.

Dependencies: Consumed by RTL8192EE C files with rtlwifi/Linux bit and type definitions.

Risks/test signals: Wrong rate or queue constants can break descriptor encoding, rate adaptation, or firmware commands. Build plus TX/RX at CCK, OFDM, and HT rates validate behavior.
