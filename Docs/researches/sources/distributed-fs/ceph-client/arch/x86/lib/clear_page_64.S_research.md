# sources/distributed-fs/ceph-client/arch/x86/lib/clear_page_64.S

Purpose: implements 64-bit page clearing and clear-user alternatives with exception handling.

Important APIs/functions: exports GPL symbol `__clear_pages_unrolled` and exported `rep_stos_alternative`. `__clear_pages_unrolled` zeros page-aligned memory in 64-byte chunks. `rep_stos_alternative` is a user-access clearing routine with the same calling convention as `rep stos`, returning remaining byte count in `%rcx`.

Control flow: `__clear_pages_unrolled` divides length by 64 and stores eight zeroed 64-bit words per loop iteration using `%rax` as zero. `rep_stos_alternative` handles small byte tails, 8-byte word stores, and 64-byte unrolled stores. Exception table entries redirect failed user stores to a tail loop or exit so `%rcx` reflects uncleared bytes as closely as practical.

State and persistence behavior: writes zeroes to kernel or user memory supplied by callers. No persistent global state. Faults can leave partially cleared memory and return remaining count.

Dependencies/integration points: 64-bit library build, usercopy/clear_user alternatives, Linux exception tables, objtool annotations, and CFI type annotations.

Risks: exception fixups must preserve the clear-user ABI. Unrolled stores can clear some bytes twice after a fault, which is accepted, but must not report success incorrectly. The page-clearing entry assumes correct alignment/length from callers.

Test signals: `clear_user` fault tests, page allocator zero-page tests, KASAN/KMSAN builds, objtool validation, and usercopy tests with faults at byte, word, and unrolled store sites.
