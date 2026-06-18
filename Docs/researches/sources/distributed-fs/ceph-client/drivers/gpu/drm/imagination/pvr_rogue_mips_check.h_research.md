<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_mips_check.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_mips_check.h

Purpose: Provides compile-time layout verification for the firmware-visible MIPS structures declared in `pvr_rogue_mips.h`.

Important APIs/types/functions: The file consists of `static_assert()` checks for field offsets and sizes of `struct rogue_mips_tlb_entry`, `struct rogue_mips_remap_entry`, and `struct rogue_mips_state`.

Control flow: No runtime flow. The compiler fails the build if any ABI-sensitive field moves or structure size changes.

State and persistence behavior: It protects persistent firmware/debug memory layout, especially `rogue_mips_state`, whose first field must be `error_state` and whose TLB/remap arrays sit at fixed offsets.

Dependencies: Includes `<linux/build_bug.h>` and relies on the structures being declared before this header is included. `pvr_rogue_mips.h` includes it at the end.

Integration points: This is an ABI guard for firmware boot and diagnostic paths that exchange binary MIPS state with host code.

Risks: Missing an assertion for a newly added firmware-visible field would allow silent ABI drift. Conversely, intentional ABI changes require updating both firmware and these asserts in lockstep.

Test signals: Kernel build success is the direct test. Cross-check with firmware dumps or boot-data readers if MIPS firmware layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_mips_check.h -->
