# sources/distributed-fs/ceph-client/arch/loongarch/lib/copy_user.S

Purpose: implements `__copy_user()` for copying between kernel and user memory with exception recovery and optimized 64-bit unaligned copy.

Important APIs, types, and functions: exported `__copy_user`, generic byte implementation `__copy_user_generic`, and 64-bit `__copy_user_fast` selected by `CPU_FEATURE_UAL`.

Control flow: generic path copies byte by byte and returns remaining bytes on fault. Fast path handles sub-9-byte sizes through a jump table, otherwise copies initial and final words, aligns destination, copies 64/32/16/8-byte chunks, and has exception-table fixups for every load/store label. Large fixup computes the remaining destination span and falls back to byte copy until another fault or completion.

State and persistence: no global state; return value is remaining byte count.

Dependencies and integration points: used by generic `copy_{to,from}_user` machinery; depends on exception-table fixups, alternative patching, CPU unaligned support, and ABI register conventions.

Risks: overlapping ranges are not `memmove`; callers must use it as usercopy. Remaining-byte accounting and load/store fault distinction are correctness-critical. Fast path assumes hardware unaligned access.

Test signals: usercopy selftests, page-boundary fault tests, short-size jump-table coverage, and copy_to/from_user stress under SMAP-like protections if applicable.
