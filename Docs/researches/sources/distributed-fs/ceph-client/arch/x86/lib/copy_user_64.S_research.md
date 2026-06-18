# sources/distributed-fs/ceph-client/arch/x86/lib/copy_user_64.S

Purpose: implements `rep_movs_alternative`, the 64-bit exception-aware user memory copy fallback for CPUs without FSRM.

Important APIs/functions: exports `rep_movs_alternative`. The calling convention matches `rep movs`: `%rdi` destination, `%rsi` source, `%rcx` count, returning remaining bytes in `%rcx`.

Control flow: small copies use byte and qword loops with exception table entries that fall back to byte-tail copying. Large copies use an alternative: ERMS CPUs can do `rep movsb`, otherwise the code aligns destination, copies qwords with `rep movsq`, and handles tails. Exception fixups return or recompute remaining bytes then retry the tail.

State and persistence behavior: partially or fully copies memory from source to destination. No global state. Faults leave `%rcx` as remaining byte count and may leave partial destination writes.

Dependencies/integration points: used by generic x86 usercopy code and alternative patching. Depends on exception-table uaccess annotations, ERMS feature detection, objtool annotations, and user access enabling by higher-level wrappers.

Risks: the ABI is intentionally tied to raw `rep movs`, so register changes can break alternative call-site rewriting. Exception fixup precision affects usercopy return values. Large-copy alignment math must not underflow counts.

Test signals: usercopy tests with page faults at source/destination, ERMS and non-ERMS CPU paths, small/large/unaligned copy cases, and copy return-count validation.
