# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-phy-db.c

Purpose: Stores PHY configuration/calibration sections received from initialization firmware and sends the collected PHY database to runtime firmware.

Important APIs and functions: Exports `iwl_phy_db_init()`, `iwl_phy_db_free()`, `iwl_phy_db_set_section()`, and `iwl_send_phy_db_data()`. Internal helpers select/free sections, validate channels, map channel IDs to PAPD/TX-power groups, retrieve section data, send `PHY_DB_CMD`, and iterate channel groups. `struct iwl_phy_db` stores config, non-channel calibration, PAPD groups, TX-power groups, and transport pointer.

Control flow: Init allocates state and marks group counts unknown. Firmware notifications call `iwl_phy_db_set_section()`, which validates payload length/type, lazily allocates group arrays using the largest group id sent first, replaces prior section data, and stores size. Runtime firmware setup calls `iwl_send_phy_db_data()`, which sends CFG, non-channel calibration, then all PAPD and TXP channel groups with data.

State and persistence: Calibration blobs are heap-copied runtime state and freed section-by-section. Group count and data arrays persist across init/runtime firmware transition but not across driver unload.

Dependencies and integration points: Uses firmware RX packet payload helpers, `iwl_trans_send_cmd()`, PHY DB firmware command structures, debug logging, and opmode/transport headers.

Risks: Set-section may run in atomic context and uses `GFP_ATOMIC`. Group allocation assumes firmware sends highest index first. Channel-to-group mapping covers classic 2.4/5GHz channels only. Missing CFG or calibration sections abort runtime send. Replacing section data must not race with send.

Test signals: Malformed notification length/type tests, group allocation failure, repeated section replacement, runtime send ordering, missing section failure, invalid channel IDs, and firmware command error propagation.
