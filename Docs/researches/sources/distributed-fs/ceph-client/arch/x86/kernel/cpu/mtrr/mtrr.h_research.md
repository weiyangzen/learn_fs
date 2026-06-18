# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/mtrr.h

Purpose: defines the private MTRR subsystem interface shared by generic, common, procfs, cleanup, and legacy backend files.

Important APIs/types/functions: defines change-mask bits `MTRR_CHANGE_MASK_FIXED`, `MTRR_CHANGE_MASK_VARIABLE`, and `MTRR_CHANGE_MASK_DEFTYPE`; debug macro `Dprintk`; `struct mtrr_ops`; and `struct set_mtrr_context`. Declares shared globals such as `mtrr_debug`, `mtrr_usage_table[]`, `mtrr_if`, `mtrr_mutex`, `num_var_ranges`, `mtrr_tom2`, `mtrr_state`, `phys_hi_rsvd`, and `changed_by_mtrr_cleanup`. Declares common helpers including `generic_get_free_region()`, `generic_validate_add_page()`, `fill_mtrr_var_range()`, `get_mtrr_state()`, `mtrr_state_warn()`, `mtrr_attrib_to_str()`, `mtrr_wrmsr()`, `mtrr_build_map()`, `mtrr_copy_map()`, `mtrr_cleanup()`, `generic_rebuild_map()`, and legacy backend ops.

Control flow: no runtime control flow beyond the inline `mtrr_enabled()`, which reports whether an active backend has been selected.

State and persistence: no state is owned here; it declares cross-file runtime state. No I/O or persistence behavior.

Dependencies and integration points: depends on `linux/types.h`, `linux/stddef.h`, MTRR constants from public asm headers, and `CONFIG_X86_32` for legacy backend declarations versus stubs. It is the local contract for every file in `arch/x86/kernel/cpu/mtrr/`.

Risks: changes to `struct mtrr_ops` affect all backends and common call sites. `mtrr_enabled()` only checks `mtrr_if`, so callers must still verify operation callbacks where needed. Conditional stubs must match the real function signatures to keep 64-bit builds correct.

Test signals: compile all x86 configurations, static analysis for all `mtrr_ops` initializers, 32-bit legacy backend symbol availability, and 64-bit stub coverage.
