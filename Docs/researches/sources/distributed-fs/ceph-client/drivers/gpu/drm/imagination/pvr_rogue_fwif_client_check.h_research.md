# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_client_check.h

Purpose: This header compile-time verifies the binary layout of client command structures from `pvr_rogue_fwif_client.h`.

Important APIs/types/functions: It defines `OFFSET_CHECK` and `SIZE_CHECK` and asserts exact offsets/sizes for `rogue_fwif_geom_regs` (64 bytes), dummy region-header init regs, `rogue_fwif_cmd_geom` (112), `rogue_fwif_frag_regs` (448), `rogue_fwif_cmd_frag` (480), `rogue_fwif_compute_regs` (72), `rogue_fwif_cmd_compute` (96), `rogue_fwif_transfer_regs` (176), and `rogue_fwif_cmd_transfer` (192).

Control flow: None at runtime. Inclusion fails the build if the compiler layout or source fields differ from the expected firmware ABI.

State and persistence behavior: No state. It protects CCCB command payload persistence by verifying register and flag offsets that firmware reads from shared command memory.

Dependencies and integration points: Depends on `linux/build_bug.h` and prior declaration of client FWIF structs. It integrates with CI/build validation for user/kernel/firmware shared command ABI.

Risks: Stale expected offsets block intended ABI updates; missing newly added fields from this file would reduce ABI coverage. Because geometry/fragment command prefixes are security-sensitive kernel patch areas, these checks are a useful guard against accidental prefix movement.

Test signals: Kernel build is the direct signal. Additional confidence comes from intentionally perturbing struct fields in review tests, cross-architecture builds, and end-to-end workload submissions after any client-command change.
