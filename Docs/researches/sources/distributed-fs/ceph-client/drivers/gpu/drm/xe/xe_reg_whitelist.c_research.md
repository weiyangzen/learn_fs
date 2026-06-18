<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.c

Purpose: defines and processes engine register whitelist entries that allow or deny userspace non-privileged MMIO access to selected registers, mainly for workarounds and OA triggers.

Important APIs and control flow: `register_whitelist[]` is an RTP save/restore table with platform/version/engine rules and `WHITELIST()` actions. `xe_reg_whitelist_process_engine()` creates an RTP engine context, processes matching entries into `hwe->reg_whitelist`, then `whitelist_apply_to_hwe()` converts each logical whitelist target into `RING_FORCE_TO_NONPRIV` save/restore entries in `hwe->reg_sr` slot order. `xe_reg_whitelist_print_entry()` decodes access mode, deny bit, and range size for debug output.

State and dependencies: depends on RTP rule matching, `xe_reg_sr_add()`, engine MMIO base, OA register definitions, platform/version helpers, and `RING_MAX_NONPRIV_SLOTS`. The generated whitelist is stored in engine-local SR tables and later applied with other engine state.

Risks and test signals: slot exhaustion logs an error and stops adding entries; tests should cover platforms with many OA/MERT entries. Whitelist range decoding and deny/access flags should be verified for both debug dump accuracy and hardware programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.c -->
