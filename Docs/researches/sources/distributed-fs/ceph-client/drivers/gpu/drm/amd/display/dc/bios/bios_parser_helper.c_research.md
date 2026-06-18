# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_helper.c

Purpose: provides shared low-level BIOS parser helpers: bounded ROM image access and BIOS scratch register helpers.

Important functions: `bios_get_image()` returns `bp->bios + offset` only when a BIOS image exists and `offset + size < bp->bios_size`; otherwise it returns `NULL`. `bios_is_accelerated_mode()` reads `BIOS_SCRATCH_6.S6_ACC_MODE`. `bios_set_scratch_acc_mode_change()` writes that field. `bios_set_scratch_critical_state()` writes `BIOS_SCRATCH_6.S6_CRITICAL_STATE`.

Control flow: parser files use the `GET_IMAGE(type, offset)` macro from the header, which delegates all pointer construction to `bios_get_image()`. Scratch helpers use `reg_helper.h` macros with `bios->ctx` and `bios->regs`.

State and persistence: ROM access is read-only and returns pointers into the parser-owned BIOS image. Scratch helpers persist state in hardware registers and are externally visible to VBIOS/driver coordination.

Dependencies and integration points: depends on `atom.h`, parser internal types, command-table headers, `reg_helper.h`, and `dc_bios` register definitions. Both parser implementations rely on this file for bounds checks and scratch state.

Risks: the bounds check uses strict `<`, so a request ending exactly at `bios_size` is rejected. Arithmetic overflow in `offset + size` would be dangerous if untrusted values reached it without wider validation. Many parser safety properties depend on every ROM pointer going through this helper. Register helpers require valid `bios->regs` and context.

Test signals: unit tests for valid, out-of-range, boundary, null BIOS, and oversized requests; register-mock tests for accelerated-mode and critical-state bit operations; parser fuzz tests that verify malformed offsets fail through `NULL` returns.
