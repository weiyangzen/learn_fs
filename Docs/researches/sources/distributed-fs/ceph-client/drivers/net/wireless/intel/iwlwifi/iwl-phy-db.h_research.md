# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-phy-db.h

Purpose: Declares the opaque PHY database API used to collect calibration notifications and replay them to runtime firmware.

Important APIs and types: Forward-declared `struct iwl_phy_db`; prototypes for `iwl_phy_db_init()`, `iwl_phy_db_free()`, `iwl_phy_db_set_section()`, and `iwl_send_phy_db_data()`.

Control flow: Callers initialize a DB for a transport, feed RX packets from calibration firmware into it, send all collected data after runtime firmware starts, and free it on teardown.

State and persistence: The header hides internal calibration storage. API users are responsible for keeping the object alive across init/runtime firmware phases and freeing it exactly once.

Dependencies and integration points: Includes opmode and transport headers for `struct iwl_trans` and `struct iwl_rx_packet`. Used by firmware-load and calibration code paths.

Risks: Opaque API makes ordering implicit; sending before required sections arrive fails. Passing RX packets from unrelated commands can corrupt or reject state.

Test signals: Compile coverage, lifecycle tests for init/set/send/free, and failure handling when set-section returns errors.
