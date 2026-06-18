# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/config.h

Purpose: Defines firmware configuration payloads for DQA enablement, TX antenna configuration, PHY calibration control, PHY-specific filter configuration, PHY configuration command versions, and DC2DC flags.

Important APIs and types: `struct iwl_dqa_enable_cmd`, `iwl_tx_ant_cfg_cmd`, `iwl_calib_ctrl`, `iwl_phy_specific_cfg`, `iwl_phy_cfg_cmd_v1`, and `iwl_phy_cfg_cmd_v3` are the main command payloads. `enum iwl_calib_cfg` enumerates calibration bitmap bits for XTAL, temperature, voltage, PAPD, TX power, DC, filters, IQ, sensitivity, chain noise, antenna coupling, DAC, ABS, and AGC.

Control flow: No local flow; callers build these structs before sending DQA, TX antenna, and PHY configuration commands.

State and persistence: No state here. Firmware persists configuration until reset or replacement command; calibration bitmaps determine firmware calibration behavior.

Dependencies and integration points: Used by firmware startup, NVM/radio configuration, ACPI WPFC filter ingestion, and command IDs in `commands.h`/datapath APIs.

Risks: Calibration bitmaps must match firmware expectations exactly. `iwl_phy_cfg_cmd_v3` extends v1 with PHY filters, so version negotiation is required. Filter chain order is LMAC1 A/B then LMAC2 A/B.

Test signals: DQA command on supported firmware, valid TX antenna masks, PHY configuration v1/v3 selection, all calibration bitmap combinations used by init/runtime firmware, ACPI WPFC filter propagation, and DC2DC flag commands.
