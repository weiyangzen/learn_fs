# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu_helper.h

Purpose: shared helper declarations and register-field macros for AMD powerplay SMU hardware managers.

Important APIs/types: declares voltage conversion, PPT array copy, register wait, power-gating preference, voltage-table, DPM-table, EVV, IRQ, AtomBIOS, dependency-table, and watermark helpers. Defines generic watermark row/table structures and `phm_get_sysfs_buf()` for sysfs buffer page alignment. Macro families perform bitfield get/set, direct/indirect/VFPF reads and writes, and direct/indirect/VFPF wait operations.

Control flow and state: macros route generated register names to CGS direct or indirect accessors and do read-modify-write for fields. No storage is defined; functions may allocate or mutate caller-owned structures.

Dependencies and integration: relies on generated AMD register naming conventions (`mmREG`, `ixREG`, `REG__FIELD_MASK`, `REG__FIELD__SHIFT`), CGS APIs, Linux page helpers, and hwmgr/AtomBIOS/PPT/DAL types included by users.

Risks and test signals: macros are unsynchronized and should not receive side-effect arguments. VFPF macros use hardware-specific `mmPORT_INDEX_11`. The header declares `phm_cf_want_microcode_fan_ctrl()` without an implementation in this paired C file. Test macro expansion through compile coverage, sysfs buffer alignment, and runtime wait/read/write paths.
