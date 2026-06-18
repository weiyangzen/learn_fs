# sources/distributed-fs/ceph-client/drivers/nvme/host/constants.c

Purpose: Provides human-readable names for NVMe I/O opcodes, admin opcodes, fabrics opcodes, and status codes when verbose NVMe error reporting is enabled.

Important APIs and flow: Static sparse arrays map opcode/status numeric constants to strings. `nvme_get_error_status_str()` masks status with `NVME_SCT_SC_MASK` and returns a known status string or `"Unknown"`. `nvme_get_opcode_str()`, `nvme_get_admin_opcode_str()`, and `nvme_get_fabrics_opcode_str()` return known opcode names or `"Unknown"` and are exported.

State and persistence behavior: No runtime mutable state and no persistent state.

Dependencies and integration points: Depends on constants from `nvme.h` and is conditionally linked into `nvme-core` by `CONFIG_NVME_VERBOSE_ERRORS`. Callers use the exported helpers for diagnostics and trace/log output.

Risks and test signals: Tables can silently fall behind new NVMe opcodes/statuses. Tests should cover unknown values, status masking, fabrics auth opcodes, and build behavior with verbose errors disabled.
