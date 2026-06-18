# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/debugfs.h

Purpose: declares the debugfs interface and small state containers used by `debugfs.c`.

Important APIs and types: exported functions cover QP file add/remove, per-device debugfs add/remove, and global debugfs root registration/unregistration. `struct bnxt_re_cc_param` binds a debugfs file to a device, offset, generation/extension selector, and dentry. `struct bnxt_re_dbg_cc_config_params` contains the gen0 CC parameter array. `struct bnxt_re_cq_coal_param` and `struct bnxt_re_dbg_cq_coal_params` perform the same role for CQ coalescing. `enum bnxt_re_cq_coal_types` indexes the coalescing fields.

Control flow and integration: no executable control flow beyond macros. The constants `CC_CONFIG_GEN_EXT()`, `CC_CONFIG_GEN0_EXT0`, and `BNXT_RE_CC_PARAM_GEN0` define how debugfs maps files to firmware modify masks.

State and persistence: the structs are runtime-only allocations hanging off `struct bnxt_re_dev`. They persist as long as the device debugfs tree exists and are freed during debugfs removal.

Dependencies: relies on forward-declared driver types from including translation units, debugfs `struct dentry`, and `bnxt_re_dev`.

Risks: enum order must match the string table and switch statements in `debugfs.c`. `BNXT_RE_CC_PARAM_GEN0` must match `bnxt_re_cc_gen0_name[]` and the supported firmware mask mapping. Any mismatch can expose the wrong knob or write the wrong firmware field.

Test signals: compile-time coverage through `debugfs.c`, runtime enumeration of expected file names, and write/read validation that each offset controls the intended firmware or CQ coalescing field.
