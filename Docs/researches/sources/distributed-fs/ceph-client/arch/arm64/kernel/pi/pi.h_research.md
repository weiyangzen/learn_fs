# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/pi.h

Purpose: this header centralizes declarations for ARM64 position-independent early boot code. It provides helpers for place-relative data references and declares the early mapping, relocation, KASLR, feature-override, dynamic SCS, and page-table construction entry points used before the fully relocated kernel is running.

Important APIs and types: `prel64_t` is a volatile signed long used for 64-bit place-relative references. `PREL64(type, name)` stores either a typed pointer or its `prel64` representation, while `prel64_pointer()` converts a `*_prel` field back to a typed pointer using `prel64_to_pointer()`. The `__prel64_initconst` section marker places such data in `.init.rodata.prel64`, which `relacheck.c` permits and rewrites from ABS64 to PREL64. Extern declarations expose `dynamic_scs_is_enabled`, `init_idmap_pg_dir`, `init_pg_dir`, `init_feature_override()`, `kaslr_early_init()`, `relocate_kernel()`, `scs_patch()`, `map_range()`, `early_map_kernel()`, and `create_init_idmap()`.

Control flow and state: `prel64_to_pointer()` returns `NULL` for a zero offset, otherwise returns `offset + *offset`. This lets early boot code dereference data even before absolute relocations are fully applied. The header itself has no persistence, but it defines the contract for early boot global page directories and the dynamic SCS flag.

Dependencies and integration: included by files in `arch/arm64/kernel/pi/`, especially relocation, early ID-register overrides, mapping, and SCS patching. It depends on core ARM64 page-table and Linux integer types being visible via surrounding translation units.

Risks: users must only apply `prel64_pointer()` to fields declared with `PREL64`; mixing absolute and place-relative storage breaks early relocation assumptions. The volatile `prel64_t` prevents undesirable compiler assumptions, but does not protect against incorrect section placement. The header is part of the early boot ABI, so signature changes ripple into assembly and boot mapping code.

Test signals: successful all-config ARM64 builds, relacheck acceptance of `.rodata.prel64`, and early boot through KASLR/relocation paths are the main signals. Failures manifest as link-time relocation guard errors, early NULL/wrong-pointer dereferences, or boot stalls in early mapping.
