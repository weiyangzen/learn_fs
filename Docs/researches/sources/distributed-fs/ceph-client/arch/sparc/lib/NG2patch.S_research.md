# sources/distributed-fs/ceph-client/arch/sparc/lib/NG2patch.S

Purpose: Runtime patcher that redirects copy operations to Niagara2 implementations.

Important APIs/functions: Defines `niagara2_patch_copyops` and a branch patch macro.

Control flow: Replaces public/default `memcpy`, `raw_copy_from_user`, and `raw_copy_to_user` entry points with branches to `NG2memcpy`, `NG2copy_from_user`, and `NG2copy_to_user`, then flushes patched instruction addresses.

State and persistence: Permanently patches kernel text during boot/runtime CPU setup.

Dependencies/integration: Depends on NG2 copy symbols and SPARC instruction encoding. Called by CPU feature selection for Niagara2-class systems.

Risks/test signals: Branch displacement and CPU selection must be correct. Test patched symbol disassembly, copy correctness after patch, and non-NG2 fallback behavior.
