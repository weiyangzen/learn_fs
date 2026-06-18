<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.h

Purpose: Defines ath9k MCI coexistence constants, channel-map/profile accounting macros, data structures, and public MCI APIs. It is the local contract between ath9k core code and AR9003 MCI Bluetooth coexistence implementation.

Important APIs and types: Constants size the scheduler and GPM DMA buffers, BT channel maps, duty cycle bounds, default aggregation limits, profile limits, and TX priority thresholds. Macros `MCI_GPM_SET_CHANNEL_BIT()` and `MCI_GPM_CLR_CHANNEL_BIT()` edit BT channel masks; `INC_PROF()`, `DEC_PROF()`, and `NUM_PROF()` maintain profile counters. Types include `struct ath_mci_profile_info`, `struct ath_mci_profile_status`, `struct ath_mci_profile`, `struct ath_mci_buf`, and `struct ath_mci_coex`. Public functions include setup/cleanup/intr/profile flush/RSSI update plus BTCOEX-gated inline stubs for `ath_mci_enable()`, `ath9k_mci_update_wlan_channels()`, and `ath9k_mci_set_txpower()`.

Control flow: The header itself has no runtime flow, but conditional compilation controls whether the main driver calls real MCI enable/channel/TX-power functions or no-op stubs when `CONFIG_ATH9K_BTCOEX_SUPPORT` is disabled.

State and persistence: Owns no global state. Its structs define runtime state stored under `sc->btcoex.mci` and `sc->mci_coex`, including profile lists, status bitmap, profile counters, aggregation limit, DMA virtual/physical addresses, and buffer lengths.

Dependencies and integration points: Includes `ar9003_mci.h` for hardware message offsets and state definitions. Used by `mci.c`, `ath9k.h` softc definitions, `main.c` MCI calls, and BTCOEX logic. The list and bitmap fields depend on Linux list/bitmap infrastructure through included driver headers.

Risks: Profile counter macros assume valid profile types and balanced increment/decrement calls; underflow would corrupt coexistence policy. Channel bit macros operate on byte offsets into a dword array and require correct BT channel bounds. Conditional stubs can hide missing BTCOEX functionality in builds without support. Buffer size constants must match AR9003 MCI hardware expectations.

Test signals: Build with and without `CONFIG_ATH9K_BTCOEX_SUPPORT`, profile counter transitions for each BT profile type, channel map bit set/clear bounds at channels 0 and 78, DMA buffer sizing against hardware setup, and callers compiling against both real and stubbed APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.h -->
