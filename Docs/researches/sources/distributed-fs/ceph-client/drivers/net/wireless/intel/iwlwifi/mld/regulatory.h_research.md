# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/regulatory.h

Purpose: declares regulatory initialization/configuration entry points for MLD firmware startup and runtime SAR profile changes.

Important APIs/types: declarations cover BIOS table loading, LARI configuration, AP type tables, TAS, PPAG, SGOM, SAR, and SAR profile configuration.

Control flow: startup paths call BIOS table loading before firmware configuration, then initialize SAR/SGOM/PPAG/LARI/AP type/TAS as supported. Runtime profile selection can call `iwl_mld_config_sar_profile()`.

State and persistence: no state is declared here. Implementations read platform ACPI/UEFI data into `mld->fwrt` and send firmware commands.

Dependencies and integration: includes local `mld.h`, tying regulatory operations to the MLD context and firmware runtime state.

Risks and test signals: callers must order table loading before command sends and respect return values where unsupported or disabled tables are nonfatal.
