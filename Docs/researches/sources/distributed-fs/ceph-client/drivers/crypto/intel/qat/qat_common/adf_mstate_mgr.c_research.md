# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_mstate_mgr.c

Purpose: provides a compact manager for building, validating, and walking QAT migration-state buffers. It writes a preamble and nested typed sections into caller-provided memory and can initialize from remote state for restore.

Important APIs: `adf_mstate_mgr_new/destroy/init`, `adf_mstate_preamble_add/update`, `adf_mstate_sect_add`, `adf_mstate_sect_add_vreg`, `adf_mstate_sect_update`, `adf_mstate_mgr_init_from_remote`, `adf_mstate_state_size`, `adf_mstate_state_size_from_remote`, and `adf_mstate_sect_lookup`.

Control flow and state: `adf_mstate_mgr` tracks `buf`, current `state` cursor, total size, and section count. Add paths reserve headers, let populate callbacks fill nested content, validate available room, then update header sizes/subsection counts and cursor. Remote init validates magic/version/header length and scans sections for bounds safety. Lookup walks section headers and optionally invokes an action callback with a sub-manager.

Dependencies and integration: used by VF live migration code to serialize ETR, BAR, config, PF/VF, and SLA state sections named by header constants.

Risks and test signals: section add failures after header reservation can leave cursor advanced; callers must treat NULL as failed state build. Test malformed remote sizes, nested section bounds, preamble version compatibility, and round-trip save/restore section lookup.
