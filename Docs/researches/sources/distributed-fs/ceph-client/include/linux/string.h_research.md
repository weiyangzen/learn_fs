# sources/distributed-fs/ceph-client/include/linux/string.h

Purpose: provides the kernel's central string and memory helper declarations, safer copy macros, user-memory duplication helpers, allocation wrappers, command-line parsers, fortify integration, and compile-time checked conversions between C strings and fixed byte arrays.

Important APIs and types: user-copy helpers include `strndup_user()`, `memdup_user()`, `vmemdup_user()`, `memdup_user_nul()`, and overflow-checked array wrappers. Core APIs cover libc-like `str*` and `mem*` operations, `strscpy()`/`strscpy_pad()`, `mem_is_zero()`, `kstrdup*()`, `kmemdup*()`, `argv_split()`, option parsing, `sysfs_streq()`, `match_string()`, binary printf helpers, `memory_read_from_buffer()`, `memzero_explicit()`, `kbasename()`, `memcpy_and_pad()`, `strtomem*()`, `memtostr*()`, `memset_after()`, `memset_startat()`, `str_has_prefix()`, `strstarts()`, and `strends()`.

Control flow: this is mostly declarative and inline/macro-driven. Callers select arch-optimized implementations through `asm/string.h`, then fall back to generic declarations when `__HAVE_ARCH_*` is absent. Safer macros use compile-time object-size, array, C-string, and non-string checks before dispatching to implementations.

State and persistence: no global state is stored here. Memory allocation helpers return kernel allocations owned by callers; `memzero_explicit()` intentionally creates a compiler-visible barrier so sensitive stack or heap data is actually cleared.

Dependencies and integration points: depends on compiler attributes, overflow checks, UAPI string definitions, fortify support, allocation hooks, sysfs semantics, command-line parsing, and arch string routines. It is used across nearly every kernel subsystem.

Risks and test signals: risks include incorrect buffer size inference, overlapping string copies, nonstring arrays treated as C strings, missed overflow checks, fortify false positives/negatives, and optimized-away security clears. Test signals include `CONFIG_FORTIFY_SOURCE`, KASAN/UBSAN, compile-time object-size diagnostics, string selftests, sysfs parser tests, and architecture build coverage.
