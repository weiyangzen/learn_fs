# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_helper.h

Purpose: exposes shared helper functions and the `GET_IMAGE` macro used by both BIOS parser generations.

Important APIs: `bios_get_image()`, `bios_is_accelerated_mode()`, `bios_set_scratch_acc_mode_change()`, and `bios_set_scratch_critical_state()`. `GET_IMAGE(type, offset)` assumes a local variable named `bp` and expands to a typed pointer from `bios_get_image(&bp->base, offset, sizeof(type))`.

Control flow and integration: parser code relies on `GET_IMAGE` for concise table reads. Scratch functions are exposed through `dc_vbios_funcs` and parser wrappers.

State, dependencies, risks, and tests: the macro’s dependency on local variable name `bp` is convenient but fragile for refactors. The header forward-declares `struct bios_parser`, but the macro accesses `bp->base`, so callers must have the internal parser definition visible. Test signals are compile coverage across all parser files and direct helper tests from `bios_parser_helper.c`.
