# sources/distributed-fs/ceph-client/arch/sparc/lib/NGpatch.S

Purpose: Runtime patcher for first-generation Niagara copy operations.

Important APIs/functions: Defines `niagara_patch_copyops`.

Control flow: Computes branch offsets and overwrites `memcpy`, `raw_copy_from_user`, and `raw_copy_to_user` entries with branches to NG implementations, followed by flushed `nop` delay slots.

State and persistence: Mutates kernel text.

Dependencies/integration: Depends on `NGmemcpy`, `NGcopy_from_user`, `NGcopy_to_user`, and CPU setup.

Risks/test signals: Patch target mistakes can break all copy operations. Validate target disassembly and run memory/user-copy tests after Niagara patching.
