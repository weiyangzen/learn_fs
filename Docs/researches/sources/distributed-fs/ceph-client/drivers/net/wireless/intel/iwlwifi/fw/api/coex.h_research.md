# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/coex.h

Purpose: Defines Bluetooth coexistence firmware command and notification ABI, including coexistence modes, enabled modules, channel inhibition, reduced TX power, activity grading, LUT selection, and profile notifications.

Important APIs and types: `struct iwl_bt_coex_cmd`, `iwl_bt_coex_reduced_txp_update_cmd`, `iwl_bt_coex_ci_cmd`, `iwl_bt_coex_prof_old_notif`, and `iwl_bt_coex_profile_notif` are the main wire structures. Enums define LUT type, coexistence mode, module bits, BT activity grading, CI compliance, and BT coexistence subcommand IDs.

Control flow: No executable flow. Runtime coexistence code sends configuration/reduced-power/CI commands and consumes profile notifications to adapt Wi-Fi behavior under BT activity.

State and persistence: Header owns no state; firmware maintains coexistence configuration and reports current BT profile. Driver may cache interpreted activity/loss values elsewhere.

Dependencies and integration points: Used by legacy command IDs in `commands.h`, BT coexistence management in DVM/MVM, regulatory/SAR power interactions, and channel/PHY configuration.

Risks: `BITS(nb)` is a local helper name that can collide if included in broad scopes. Old and new profile notification layouts differ substantially. Reduced TX power encodes enable bit and station ID in one field. Loss arrays are band/chain indexed and depend on `COEX_NUM_BAND` and `COEX_NUM_CHAINS`.

Test signals: Enable/disable coexistence modes and modules, reduced TX power per station, CI primary/secondary bitmaps, old profile notification v4/v5 parsing, new profile loss arrays, and high BT traffic adaptation.
