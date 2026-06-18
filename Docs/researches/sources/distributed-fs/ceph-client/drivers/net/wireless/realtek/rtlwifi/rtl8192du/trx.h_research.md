# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/trx.h

Purpose: Provides RTL8192DU TX queue constants, TX page-budget constants, local descriptor bitfield setters, and TRX function declarations.

Important APIs/definitions: `TX_SELE_HQ/LQ/NQ` identify USB output queue-selection bits. Page macros describe normal and dual-MAC queue budgets. Inline setters update descriptor BMC, aggregation-break, and checksum fields. Declarations expose TX descriptor fill, endpoint mapping, queue mapping, aggregation, cleanup, and post-URB hooks.

Control flow/integration: `trx.c` implements the declarations and uses the inline setters. `sw.c` registers the functions into HAL and USB config. Common descriptor setters from `trx_common.h` complement these helpers.

State and persistence: Header is stateless; inline helpers mutate caller-provided descriptor memory.

Dependencies: Requires Linux bit macros, `__le32`, mac80211/USB types, and rtlwifi queue constants.

Risks/test signals: Bit positions must match hardware. Build with rtl8192du and test TX, AMPDU, BMC frames, and endpoint mapping.
