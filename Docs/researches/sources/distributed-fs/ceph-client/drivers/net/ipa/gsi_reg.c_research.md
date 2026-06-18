# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_reg.c

Purpose: Implements GSI register description selection, register-ID validation for each IPA/GSI version, and I/O mapping of the `gsi` memory resource.

Important APIs/functions: `gsi_reg()` validates a requested `enum gsi_reg_id` against the current version and returns its `struct reg` descriptor. `gsi_reg_init()` obtains the named platform memory resource `gsi`, checks it fits in 32-bit address math, selects the version-specific `struct regs`, and maps it with `ioremap()`. `gsi_reg_exit()` unmaps and clears pointers.

Control flow: During `gsi_init()`, `gsi_reg_init()` runs before any GSI register access. The version switch maps IPA v3.1 to `gsi_regs_v3_1`, v3.5.1 to `gsi_regs_v3_5_1`, v4.2 to `gsi_regs_v4_0`, v4.5/v4.7 to `gsi_regs_v4_5`, v4.9 to `gsi_regs_v4_9`, v4.11 to `gsi_regs_v4_11`, and v5.x to `gsi_regs_v5_0`. Later GSI code calls `gsi_reg()` for every register access.

State and persistence: Mutates `gsi->regs` and `gsi->virt`; both are cleared on exit. No persistent storage is used.

Dependencies: Depends on platform resources, Linux I/O mapping, `gsi.h`, `gsi_reg.h`, and generic `reg.h` helpers. It also depends on version-specific register tables defined elsewhere under the IPA register data.

Risks: Invalid version mapping or register validity rules can make later code read/write wrong offsets. The `WARN()` in `gsi_reg()` returns NULL for invalid IDs, so callers must not request gated registers on unsupported versions. Resource address range validation assumes 32-bit GSI offsets.

Test signals: Probe should fail clearly on missing `gsi` DT resource, unsupported IPA version, or failed remap. Version smoke tests should exercise IPA 3.5.1, 4.2, 4.9, 4.11, and 5.x paths so gated registers such as `HW_PARAM_4` are used only when valid.
