# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/debugfs.c

Purpose: implements debugfs support for `bnxt_re`, including per-device directories, per-QP inspection files, resource/pacing info, congestion-control tunables, and CQ coalescing tunables.

Important APIs and functions: module-level `bnxt_re_register_debugfs()` and `bnxt_re_unregister_debugfs()` create/remove `/sys/kernel/debug/bnxt_re`. Per-device lifecycle is handled by `bnxt_re_debugfs_add_pdev()` and `bnxt_re_debugfs_rem_pdev()`. Per-QP entries are added and removed with `bnxt_re_debug_add_qpinfo()` and `bnxt_re_debug_rem_qpinfo()`. `info_show()` reports resource watermarks and doorbell pacing counters. `bnxt_re_cc_config_get()`/`bnxt_re_cc_config_set()` query and modify firmware congestion-control parameters. `cq_coal_cfg_show()`/`cq_coal_cfg_write()` expose CQ interrupt coalescing knobs when supported.

Control flow: device debugfs creation builds the PCI-device directory, `QPs`, `cc_config`, the `info` file, and optional `cq_coal_cfg`. QP creation adds a read-only file named by QPN; reading it formats transport type, state, MTU, timeout, remote QPN, and rate-limit status. CC reads issue `bnxt_qplib_query_cc_param()`, map an offset to a field, and return the value; writes parse a u32, fill one modified field and mask, then call `bnxt_qplib_modify_cc()`. CQ coalescing writes validate ranges before mutating `rdev->cq_coalescing`.

State and persistence: debugfs entries are ephemeral and removed on driver/device teardown. Some writes modify persistent runtime device state: CC writes program firmware state, while CQ coalescing writes update `rdev->cq_coalescing` used by future or active CQ handling. Allocated parameter arrays live in `rdev->cc_config_params` and `rdev->cq_coal_cfg_params`.

Dependencies and integration points: depends on Linux debugfs, seq_file, user-copy parsing, qplib SP firmware calls, qplib FP constants, `bnxt_re` device state, and `ib_verbs.h` QP structures. It is integrated from QP create/destroy paths and main device registration/removal.

Risks: debugfs write handlers are privileged but still need strict range checking. `bnxt_re_debugfs_add_pdev()` allocates `cc_config_params` but does not explicitly guard allocation failure before indexing. CC parameter name arrays and `BNXT_RE_CC_PARAM_GEN0` must stay in sync. Cleanup must handle optional CQ coalescing directories and partially initialized devices. QP debug reads allocate a formatted buffer and reject short user buffers with `-ENOSPC`, which differs from normal partial-read behavior.

Test signals: mount-debugfs inspection, per-QP file creation/removal during QP churn, read/write tests for every CC and CQ coalescing file including invalid values, firmware error injection for CC query/modify, remove paths after partial initialization, and lockdep/KASAN during concurrent QP destroy and debugfs reads.
