# sources/distributed-fs/ceph-client/arch/sparc/lib/U3patch.S

Purpose: Runtime patcher for UltraSPARC-III/Cheetah copy operations.

Important APIs/functions: Defines `cheetah_patch_copyops`.

Control flow: Replaces default/public `memcpy`, `raw_copy_from_user`, and `raw_copy_to_user` entries with branches to U3/Cheetah routines and flushes patched instructions.

State and persistence: Mutates kernel text.

Dependencies/integration: Depends on U3 implementation symbols and CPU detection.

Risks/test signals: Incorrect patching breaks fundamental memory operations. Validate branch targets, boot-time CPU selection, and copy tests after patch.
