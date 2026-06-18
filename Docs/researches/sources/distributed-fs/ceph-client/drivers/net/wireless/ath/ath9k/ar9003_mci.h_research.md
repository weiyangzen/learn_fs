# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_mci.h

## Purpose
`ar9003_mci.h` is the protocol contract for AR9003 MCI Bluetooth coexistence. It defines the MCI message headers, coex-agent GPM layout, calibration message subtypes, BT state values, state-query IDs, configuration bitfields, antenna architecture encodings, helper macros for packed GPM payloads, and public function prototypes.

## Important APIs, Types, and Defines
Important enums include `mci_message_header`, `mci_gpm_subtype`, `mci_bt_state`, `mci_ps_state`, `mci_state_type`, `mci_gpm_coex_opcode`, `mci_gpm_coex_query_type`, `mci_gpm_coex_halt_bt_gpm`, and `mci_gpm_coex_bt_update_flags_op`. The header also defines coex profile IDs and GPM byte offsets for version, status query, WLAN channels, profile info, status update, and BT flag update messages.

Key macros are `MCI_GPM_TYPE()`, `MCI_GPM_OPCODE()`, `MCI_GPM_SET_CAL_TYPE()`, `MCI_GPM_SET_TYPE_OPCODE()`, `MCI_GPM_RECYCLE()`, and `MCI_GPM_IS_CAL_TYPE()`. Configuration bits such as `ATH_MCI_CONFIG_DISABLE_MCI`, `ATH_MCI_CONFIG_DISABLE_MCI_CAL`, `ATH_MCI_CONFIG_DISABLE_OSLA`, `ATH_MCI_CONFIG_DISABLE_FTP_STOMP`, `ATH_MCI_CONFIG_CONCUR_TX`, `ATH_MCI_CONFIG_ANT_ARCH`, and debug/observation flags drive behavior in `ar9003_mci.c`.

## Control Flow
The header itself has no runtime control flow, but it defines the inputs that drive the implementation. Callers use the always-declared MCI core functions for message send, setup, cleanup, interrupt retrieval, GPM walking, BT version updates, and WLAN channel publishing. Under `CONFIG_ATH9K_BTCOEX_SUPPORT`, the hardware-reset and calibration helpers are real external functions. Without that option, most helpers compile to no-ops or conservative return values, allowing common ath9k code to call them unconditionally.

## State and Persistence Behavior
The header does not allocate state. It names transient driver states and packed on-wire/in-ring values. `MCI_GPM_RECYCLE()` mutates a consumed GPM entry by writing the reserved pattern into its payload word, so the macro is part of the ring state protocol and not a pure accessor. `MCI_2G_FLAGS_*` and `MCI_5G_FLAGS_*` encode the state transition between 2 GHz coexistence mode and 5 GHz/non-shared mode.

## Dependencies and Integration Points
The header depends on common kernel/ath9k bit macros such as `BIT()`, `MS()`, and the forward declarations visible through included ath9k headers. It is included by `mci.h`, `ar9003_mci.c`, AIC/calibration/MAC/eeprom code, and reset paths. Public prototypes are also referenced indirectly by WoW power-save handling and by eeprom transmit-power logic through `ar9003_mci_get_max_txpower()` when BT concurrent TX constrains maximum power.

## Risks
The enum `mci_state_type` is broader than the implementation in `ar9003_mci_state()`. New callers can assume a state ID is implemented because it is declared here, but unhandled cases silently return zero. GPM byte offsets are hard-coded and endian/layout sensitive because the implementation casts `u32 *` payloads to `u8 *`. Some no-op stubs have signatures that differ slightly from the enabled implementation, notably the disabled `ar9003_mci_reset()` stub returning `void` while the enabled prototype returns `int`; callers in compiled configurations must match what the preprocessor exposes.

## Test Signals
Compile coverage should include both `CONFIG_ATH9K_BTCOEX_SUPPORT=y` and disabled builds to verify prototypes/stubs remain compatible. Protocol-level tests should validate GPM type/opcode packing, recycle marker behavior, 2G/5G flag masks, and antenna architecture predicates. Runtime logs from `ar9003_mci.c` are the practical signal that the constants here match hardware and BT firmware expectations.
