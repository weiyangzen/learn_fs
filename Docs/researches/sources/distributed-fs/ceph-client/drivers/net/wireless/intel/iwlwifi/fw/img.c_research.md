<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.c

Purpose: lookup helpers for firmware command/notification versions, BIOS-supported command table revisions, and assert id descriptions.

Important APIs/functions: `iwl_fw_lookup_cmd_bios_supported_revision()` selects ACPI or UEFI max revision for a command. `iwl_fw_lookup_cmd_ver()` and `iwl_fw_lookup_notif_ver()` scan parsed `iwl_fw_cmd_version` entries. `iwl_fw_lookup_assert_desc()` maps common assert ids, masking CPU bits, to strings such as `SYSASSERT`, `BAD_COMMAND`, and `PNVM_MISSING`.

Control flow: command ids are normalized into group/opcode pairs, treating group 0 as `LONG_GROUP` for older command API assumptions. Missing tables, unknown entries, unsupported BIOS source, or `IWL_FW_CMD_VER_UNKNOWN` return the caller-provided default.

State and persistence: stateless lookups over parsed `struct iwl_fw` capability arrays. The assert string table is static.

Dependencies/integration: used by debugfs firmware info, DHC helpers, runtime init commands, regulatory code, dump logging, timestamp marker handling, and many op-mode command-version branches.

Risks/test signals: default handling is critical because callers use version thresholds to choose binary command formats. Test group-zero normalization, unknown sentinel behavior, ACPI vs UEFI revision selection, duplicate/missing entries, and assert id masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.c -->
