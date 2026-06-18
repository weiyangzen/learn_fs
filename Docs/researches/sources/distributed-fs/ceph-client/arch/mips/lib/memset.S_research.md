# sources/distributed-fs/ceph-client/arch/mips/lib/memset.S

Purpose: implements optimized MIPS `memset` and `__bzero` with user/EVA exception fixups.

Important APIs/functions: exports `memset` and `__bzero`; macros include `f_fill64`, `__BUILD_BZERO`, and exception wrapper `EX`.

Control flow: `memset` expands byte fill into a word/dword pattern, then the generated bzero/fill body handles small regions bytewise, aligns the destination, writes unrolled 64-byte blocks, writes partial words, and handles tail bytes. Exception fixups return remaining unset byte counts for bzero/user-style paths.

State and persistence: mutates destination memory only.

Dependencies and integration: core kernel memory primitive; depends on MIPS store-left/right support or byte fallback, microMIPS handling, EVA, exception tables, and R10K barriers.

Risks: alignment and fixup accounting are subtle. Incorrect fill expansion or store-left/right use corrupts memory; missing barriers can affect affected CPUs.

Test signals: string/memory selftests, fault-injection for bzero/user mappings, microMIPS and EVA builds, and boot memory initialization.
