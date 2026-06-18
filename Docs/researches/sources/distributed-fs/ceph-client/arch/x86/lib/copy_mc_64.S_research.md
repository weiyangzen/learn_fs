# sources/distributed-fs/ceph-client/arch/x86/lib/copy_mc_64.S

Purpose: provides 64-bit assembly backends for machine-check-safe copying: a fragile conservative copy loop and an enhanced fast-string copy with exception recovery.

Important APIs/functions: defines `copy_mc_fragile` under `CONFIG_X86_MCE` and `copy_mc_enhanced_fast_string` outside UML. `copy_mc_fragile` returns zero on success or remaining bytes on read/write exception. `copy_mc_enhanced_fast_string` performs `rep movsb` and returns `%rcx` bytes remaining on exception.

Control flow: fragile copy aligns the source to 8 bytes with byte copies, copies aligned 8-byte words, then trailing bytes. Read exceptions on leading/word/trailing loads compute remaining byte count. Write exceptions on word stores call `copy_mc_fragile_handle_tail()` to probe the exact destination fault point. Enhanced fast-string sets `%rcx` from length, performs `rep movsb`, and exception-table fixup returns the remaining count.

State and persistence behavior: modifies destination memory partially or fully. No global state. Exception table metadata controls recovery behavior.

Dependencies/integration points: called by `copy_mc.c`, depends on Linux exception tables with `EX_TYPE_DEFAULT_MCE_SAFE`, x86 assembly/linkage, MCE recovery capability, and uaccess wrappers where destination is user memory.

Risks: exception fixup labels and remaining-byte calculations are correctness-critical. Fragile copy intentionally avoids dangerous fast-string cases but still assumes poison alignment properties. Enhanced fast-string should only be used on CPUs whose MCE recovery supports it.

Test signals: poison-copy fault injection across byte, word, and cacheline boundaries; write-fault tests; ERMS fast-string fault tests; and build coverage with `CONFIG_X86_MCE` and UML exclusions.
