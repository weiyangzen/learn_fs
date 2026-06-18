# sources/distributed-fs/ceph-client/arch/sparc/lib/GENpatch.S

Purpose: Runtime patcher that redirects default Ultra-I copy routines to generic SPARC64 copy routines.

Important APIs/functions: Defines `generic_patch_copyops` and macro `GEN_DO_PATCH(OLD, NEW)`.

Control flow: For each old entry (`memcpy`, `raw_copy_from_user`, `raw_copy_to_user`), computes the relative branch displacement to the new generic implementation, writes a `ba` instruction over the old entry, writes a `nop` delay slot, and flushes the patched instruction.

State and persistence: Persistently mutates kernel text. No separate data state.

Dependencies/integration: Depends on `GENmemcpy`, `GENcopy_from_user`, `GENcopy_to_user`, SPARC instruction encoding, and CPU setup code that invokes this patcher.

Risks/test signals: Bad displacement math can redirect execution into invalid text. Test that patched symbols land on the expected functions, copying still works after boot patching, and instruction cache flushes are sufficient on target hardware.
