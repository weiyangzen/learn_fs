# Group Research: group_1206_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_stdlib_malloc_c_sourc_d39673395338

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/malloc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/malloc.c

Read completely: 1312 lines.

Implements NetBSD libc's historical PHK/FreeBSD-derived allocator. It uses `sbrk`/`brk` for heap pages, an mmap-backed page directory for ownership metadata, page-run records for large allocations, and page-local chunk bitmaps for small power-of-two buckets.

Initialization derives page geometry, parses `/etc/malloc.conf`, `MALLOC_OPTIONS` when safe, and `_malloc_options`, and configures abort, junk fill, zero fill, SysV `malloc(0)`, realloc behavior, xmalloc, `madvise`, and utrace modes. Public `malloc`, `calloc`, `realloc`, `free`, and `posix_memalign` funnel through `pubrealloc()` for locking, recursion detection, initialization, tracing, and zero-size sentinel handling.

The allocator contains many corruption checks for bad pointers, modified page/chunk pointers, double frees, and damaged free lists. It is legacy global-state code with non-recursive locking; signal-time recursive allocation fails with `EINVAL`. `calloc()` checks multiplication overflow, while `posix_memalign()` only supports alignments up to the page size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/merge.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/merge.c

Read completely: 396 lines.

Implements stable `mergesort()` and `mergesort_r()`. It allocates a temporary array, detects initial natural or pairwise runs in `setup()`, and repeatedly merges linked run lists between source and scratch buffers.

The merge loop uses linear then exponential/binary search to skip ordered spans, and copy macros specialize aligned int-sized records with byte fallback. `mergesort()` adapts the traditional comparator through a cookie shim. It returns `-1` for invalid element sizes or allocation failure and preserves stable ordering.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/merge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/mrand48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/mrand48.c

Read completely: 33 lines.

Implements `mrand48()` using the shared global `__rand48_seed`. It advances the 48-bit LCG via `__dorand48()` and returns a signed `long` built from the high seed words.

This is not independently reentrant because it mutates global rand48 state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/mrand48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/nrand48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/nrand48.c

Read completely: 38 lines.

Implements `nrand48(unsigned short xseed[3])`. It asserts a non-null caller seed, advances it with `__dorand48()`, and returns a non-negative 31-bit-style value from the upper seed bits.

Unlike `mrand48()`, state is caller-supplied, so the generator state can be used reentrantly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/nrand48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/posix_openpt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/posix_openpt.c

Read completely: 46 lines.

Implements `posix_openpt(int oflag)` as `open("/dev/ptmx", oflag)`. It is a thin POSIX pty master wrapper with no local flag filtering, permission handling, or retry behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/posix_openpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/pty.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/pty.c

Read completely: 81 lines.

Implements `grantpt()`, `unlockpt()`, `ptsname()`, and `ptsname_r()`. `grantpt()` uses `TIOCGRANTPT`, `unlockpt()` returns success, and both name functions use `TIOCPTSNAME`.

`ptsname()` returns a pointer into static storage and is not thread-safe. `ptsname_r()` copies into caller storage and returns error numbers, but its truncation test uses `strlcpy(...) > buflen`, which misses the exact-truncation case where the return equals `buflen`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/pty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/putenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/putenv.c

Read completely: 82 lines.

Implements `putenv(char *str)` through NetBSD environment helpers. It validates `NAME=value`, write-locks the environment, finds or creates the slot, frees any owned old entry, and stores the caller's string pointer directly.

The function follows `putenv(3)` ownership semantics: the supplied buffer becomes the environment entry and must remain valid.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/putenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/qabs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/qabs.c

Read completely: 52 lines.

Implements `qabs(quad_t)` as a simple negative test and negation. Like other signed absolute-value helpers, negating the most negative representable value has signed overflow behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/qabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/qdiv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/qdiv.c

Read completely: 65 lines.

Implements `qdiv(quad_t num, quad_t denom)` returning `qdiv_t`. It computes native quotient and remainder, then adjusts the pair when a non-negative numerator has a negative remainder.

There is no denominator validation; division by zero remains caller error.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/qdiv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/qsort.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/qsort.c

Read completely: 203 lines.

Implements `qsort()` and `qsort_r()` using Bentley/McIlroy quicksort. It uses median-of-three and pseudomedian-of-nine pivot selection, partitions equal keys to both ends, vec-swaps equal ranges back, and recurses on the smaller side while tail-iterating the larger side.

Small partitions use insertion sort. Swapping specializes aligned long-sized elements and falls back to byte swaps. The sort is in-place and unstable.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/qsort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/quick_exit.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/quick_exit.c

Read completely: 93 lines.

Implements C11 `at_quick_exit()` and `quick_exit()`. Handlers are malloc-backed nodes on a singly linked stack, protected by `__atexit_mutex` while registering in reentrant builds, and invoked in reverse registration order before `_Exit(status)`.

The traversal in `quick_exit()` is not locked and the code does not implement C++ exception termination behavior beyond an XXX note.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/quick_exit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/radixsort.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/radixsort.c

Read completely: 331 lines.

Implements `radixsort()` and `sradixsort()` for arrays of byte-string pointers. `radixsort()` uses unstable in-place American flag-style radix sorting with a bounded stack; `sradixsort()` allocates a temporary pointer array for stable distribution.

Both functions build or consume a translation table and validate `endch` when a custom table is used. Small bins use insertion sort, and recursive fallback is used when stack capacity would be exceeded.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/radixsort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand.c

Read completely: 56 lines.

Implements `rand()` and `srand()` with the classic linear congruential formula `next = next * 1103515245 + 12345`. State is a single static `u_long`, so the interface is process-global and not thread-independent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand48.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand48.h

Read completely: 34 lines.

Defines internal rand48 declarations and constants. It exposes `__dorand48`, global seed/multiplier/addend arrays, and the default POSIX rand48 seed, multiplier, and addend constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand48.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand_r.c

Read completely: 51 lines.

Implements `rand_r(unsigned int *seed)` with the same LCG family as `rand()`, updating caller-provided state and returning the masked `RAND_MAX` range. It is reentrant with respect to generator state but remains a weak-quality historical PRNG.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/reallocarr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/reallocarr.c

Read completely: 95 lines.

Implements `reallocarr(void *ptr, size_t number, size_t size)` when the platform lacks it. The pointer-to-pointer argument is accessed by `memcpy`, preserving aliasing rules, and zero dimensions free the old allocation and store NULL.

It detects multiplication overflow with a fast square-root threshold check plus division fallback, returns `EOVERFLOW` on overflow, and preserves the caller's incoming `errno`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/reallocarr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/reallocarray.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/reallocarray.c

Read completely: 63 lines.

Implements `reallocarray(void *optr, size_t nmemb, size_t size)` on top of `reallocarr()`. Zero dimensions delegate to `realloc(optr, 0)`, successful allocation returns the updated pointer, and `EOVERFLOW` is mapped to `errno = ENOMEM`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/reallocarray.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/remque.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/remque.c

Read completely: 53 lines.

Implements `remque(void *element)` for legacy doubly linked queues with `q_forw` and `q_back` fields. It patches neighboring links if present but does not clear the removed element's own pointers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/remque.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/seed48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/seed48.c

Read completely: 49 lines.

Implements `seed48()`. It saves the old global rand48 seed in static storage, installs the caller seed, resets multiplier/addend constants, and returns the static old-seed buffer.

The returned buffer is overwritten on subsequent calls and the global rand48 state is not thread-independent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/seed48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/setenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/setenv.c

Read completely: 127 lines.

Implements `setenv(name, value, rewrite)` with NetBSD environment locking and allocation helpers. It validates the name, locates or creates a slot, honors `rewrite == 0`, reuses owned buffers when possible, otherwise allocates a `name=value` string and frees any owned old value.

Concurrency and ownership are delegated to `env.h`/`local.h` helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/setenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/srand48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/srand48.c

Read completely: 38 lines.

Implements `srand48(long seed)`. It initializes the global rand48 seed from the fixed low seed word and the supplied upper 32 bits, then resets multiplier and addend constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/srand48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strfmon.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strfmon.c

Read completely: 680 lines.

Implements `strfmon()` and `strfmon_l()` through internal `vstrfmon_l()`. It parses monetary format flags, width, left/right precision, national vs international currency selection, sign placement, grouping suppression, padding, and left justification.

Formatting uses `localeconv_l()`, duplicates the currency symbol, formats the absolute double value with `asprintf_l()`, applies monetary decimal/thousands separators and grouping rules, then composes signs, symbol, value, spaces, parentheses, and field padding into the caller buffer. It returns `-1` with `E2BIG`, `EINVAL`, or allocation errors on failure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strfmon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strsuftoll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strsuftoll.c

Read completely: 252 lines.

Implements `strsuftoll()` and `strsuftollx()` when unavailable. It parses positive decimal values with optional suffix multipliers `b`, `k`, `m`, `g`, `t`, and `w`, and supports product expressions separated by `x` or `*`.

`strsuftoll()` exits with `errx()` on error, while `strsuftollx()` returns messages in a caller buffer. The recursive product parser has a depth limit of 16 and performs overflow and min/max checks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strsuftoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtol.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtol.c

Read completely: 45 lines.

Instantiates the shared `_strtol.h` template for `strtol`. It defines the function name and signed integer bounds as `long`, `LONG_MIN`, and `LONG_MAX`, relying on the included template for parsing and overflow behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtonum.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtonum.c

Read completely: 84 lines.

Implements OpenBSD-style `strtonum()`. It calls `strtoi()` with base 10 and caller min/max bounds, maps clean success to NULL error string, maps range errors to `"too large"` or `"too small"` when the whole string parsed, and returns `"invalid"` otherwise.

Unexpected `strtoi()` status causes `abort()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtonum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtoq.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtoq.c

Read completely: 44 lines.

Instantiates `_strtol.h` for historical signed quad conversion. It defines `_FUNCNAME` as `strtoq`, the integer type as `quad_t`, and bounds as `QUAD_MIN`/`QUAD_MAX`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtoq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtouq.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtouq.c

Read completely: 43 lines.

Instantiates `_strtoul.h` for historical unsigned quad conversion. It defines `_FUNCNAME` as `strtouq`, the unsigned type as `u_quad_t`, and the bound as `UQUAD_MAX`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtouq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/system.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/system.c

Read completely: 141 lines.

Implements `system()`. A NULL command checks execute access to `_PATH_BSHELL`; otherwise the parent ignores `SIGINT`/`SIGQUIT`, blocks `SIGCHLD`, and spawns `/bin/sh -c -- command` with `posix_spawn()`.

The child signal defaults and mask are set through spawn attributes so `SIGINT`/`SIGQUIT` are reset unless the caller already ignored them. Environment access is read-locked around `posix_spawn()`, and the parent waits with `waitpid()` retrying `EINTR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/system.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/tdelete.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/tdelete.c

Read completely: 66 lines.

Implements `tdelete()` for the `search.h` binary search tree API. It searches by comparator, unlinks the matching node, handles zero, one, or two child cases by selecting the right subtree successor, frees the deleted node, and returns the parent node pointer as specified by the historical interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/tdelete.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/tfind.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/tfind.c

Read completely: 47 lines.

Implements `tfind()` for `search.h` trees. It walks left or right according to the comparator until a matching node or NULL branch is found, returning the node pointer or NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/tfind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/tsearch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/tsearch.c

Read completely: 56 lines.

Implements `tsearch()`. It searches the binary tree and returns an existing matching node, or allocates and links a new `node_t` containing the caller key pointer when no match exists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/tsearch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/twalk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/twalk.c

Read completely: 53 lines.

Implements `twalk()` recursive traversal for `search.h` trees. Leaf nodes receive `leaf`; internal nodes receive `preorder`, `postorder`, and `endorder` callbacks around left and right recursion with increasing depth.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/twalk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/unsetenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/unsetenv.c

Read completely: 105 lines.

Implements `unsetenv(name)`. It validates the name, write-locks the environment, finds the first matching slot, frees owned matching values, compacts nonmatching entries down, clears stale tail slots, and unlocks.

Removing an absent variable is a successful no-op.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/unsetenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_bcmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_bcmp.c

Read completely: 15 lines.

Lint stub for `bcmp()`. It declares the function with correct signature and returns `0`; it is for lint/interface checking, not runtime implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_bcmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_bcopy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_bcopy.c

Read completely: 14 lines.

Lint stub for `bcopy()`. It provides the public signature and an empty body for lint analysis.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_bcopy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_bzero.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_bzero.c

Read completely: 14 lines.

Lint stub for `bzero()`. It declares the interface and performs no operation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_bzero.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_ffs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_ffs.c

Read completely: 15 lines.

Lint stub for `ffs()`. It provides the signature from `<strings.h>` and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_ffs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_index.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_index.c

Read completely: 15 lines.

Lint stub for historical `index()`. It declares the interface and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_index.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memccpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memccpy.c

Read completely: 15 lines.

Lint stub for `memccpy()`. It preserves the public signature and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memccpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memchr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memchr.c

Read completely: 15 lines.

Lint stub for `memchr()`. It declares the interface and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memchr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memcmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memcmp.c

Read completely: 15 lines.

Lint stub for `memcmp()`. It declares the interface and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memcmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memcpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memcpy.c

Read completely: 15 lines.

Lint stub for `memcpy()`. It preserves the signature and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memcpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memmove.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memmove.c

Read completely: 15 lines.

Lint stub for `memmove()`. It declares the interface and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memmove.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memset.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memset.c

Read completely: 15 lines.

Lint stub for `memset()`. It provides the public signature and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_rindex.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_rindex.c

Read completely: 15 lines.

Lint stub for historical `rindex()`. It declares the interface and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_rindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strcat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strcat.c

Read completely: 15 lines.

Lint stub for `strcat()`. It preserves the signature and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strcat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strchr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strchr.c

Read completely: 15 lines.

Lint stub for `strchr()`. It declares the interface and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strchr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strcmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strcmp.c

Read completely: 15 lines.

Lint stub for `strcmp()`. It declares the interface and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strcmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strcpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strcpy.c

Read completely: 15 lines.

Lint stub for `strcpy()`. It preserves the signature and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strcpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strlen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strlen.c

Read completely: 15 lines.

Lint stub for `strlen()`. It declares the interface and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strlen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strncat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strncat.c

Read completely: 15 lines.

Lint stub for `strncat()`. It provides the public signature and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strncat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strncmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strncmp.c

Read completely: 15 lines.

Lint stub for `strncmp()`. It declares the interface and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strncmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strncpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strncpy.c

Read completely: 15 lines.

Lint stub for `strncpy()`. It preserves the signature and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strncpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strrchr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strrchr.c

Read completely: 15 lines.

Lint stub for `strrchr()`. It declares the interface and returns NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_strrchr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_swab.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_swab.c

Read completely: 14 lines.

Lint stub for `swab()`. It provides the signature and an empty body.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Lint_swab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Makefile.inc

Read completely: 95 lines.

Build fragment for libc string sources. It sets `.PATH`, lists narrow string, memory, popcount, explicit memset, constant-time compare, wide-character, and architecture-overridable sources, and adds per-file compiler flags.

It includes the architecture string `Makefile.inc`, declares man pages, and adds many manual-page links for aliases such as `index`, `rindex`, `strlcpy`, `strtok_r`, `strerror_r`, and wide-character functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/__strsignal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/__strsignal.c

Read completely: 97 lines.

Implements internal `__strsignal(int num, char *buf, size_t buflen)`. For known signals it returns `sys_siglist[num]` directly without NLS, or copies localized text into the buffer with NLS enabled.

Unknown values are formatted as `"Unknown signal: %u"`, and realtime signals in range are formatted separately. The function converts the input to unsigned, so negative signals become large unknown signal numbers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/__strsignal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/bm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/bm.c

Read completely: 230 lines.

Implements the Boyer-Moore search helper API `bm_comp()`, `bm_exec()`, and `bm_free()`. Compilation copies the pattern, builds a 256-entry bad-character delta table, selects a rare-character guard from a default or caller frequency table, and computes an additional match-shift value.

`bm_exec()` searches a byte buffer using fast skip loops, rare-character guard tests, and forward verification. Zero-length patterns are rejected with `EINVAL`; allocation failures unwind through `bm_free()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/bm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/index.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/index.c

Read completely: 3 lines.

Compatibility wrapper for historical `index()`. It defines `INDEX` and includes `strchr.c`, causing the shared implementation to build the alias variant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/index.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/memccpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/memccpy.c

Read completely: 61 lines.

Implements `memccpy()`. It copies bytes from source to destination until either `n` bytes are copied or byte `c` is copied, returning the destination pointer just past the copied sentinel or NULL if not found.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/memccpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/mempcpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/mempcpy.c

Read completely: 46 lines.

Provides `mempcpy()` when unavailable. It delegates to `memcpy(dst, src, len)` and returns `dst + len`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/mempcpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/memrchr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/memrchr.c

Read completely: 54 lines.

Implements `memrchr()`. It scans a memory region backward from `s + n` for byte `c`, returning the last matching address or NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/memrchr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/rindex.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/rindex.c

Read completely: 3 lines.

Compatibility wrapper for historical `rindex()`. It defines `RINDEX` and includes `strrchr.c` to build the alias variant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/rindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/stpcpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/stpcpy.c

Read completely: 56 lines.

Implements `stpcpy()`. It copies a NUL-terminated string from source to destination and returns a pointer to the terminating NUL in the destination.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/stpcpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/stpncpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/stpncpy.c

Read completely: 54 lines.

Implements `stpncpy()`. It copies up to `n` bytes, NUL-padding after an early source terminator, and returns the destination pointer at the copied terminator or at `dst + n` when no terminator is copied.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/stpncpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strcasestr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strcasestr.c

Read completely: 69 lines.

Implements case-insensitive substring search. It lowercases the first needle character for candidate selection, then uses `strncasecmp()` on the remainder of the needle.

The implementation is straightforward O(n*m)-style scanning and uses the current C/POSIX character classification behavior of `tolower`/`strncasecmp`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strcasestr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strcoll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strcoll.c

Read completely: 72 lines.

Implements `strcoll()` and `strcoll_l()`. Because LC_COLLATE is marked unimplemented, `strcoll_l()` ignores the locale and returns `strcmp(s1, s2)`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strcoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strdup.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strdup.c

Read completely: 65 lines.

Implements `strdup()`. It computes `strlen(str) + 1`, allocates with `malloc()`, copies the complete string including NUL with `memcpy()`, and returns the new buffer or NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strdup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strerror.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strerror.c

Read completely: 98 lines.

Implements `strerror()` and `strerror_l()` as wrappers around `_strerror_lr()`. In reentrant builds it uses a thread-specific buffer allocated once per thread, falling back to a static buffer if allocation fails; non-reentrant builds use a static buffer.

`strerror_l()` sets `errno` if `_strerror_lr()` reports an error, and returns the buffer containing either a known error message or an unknown-error string.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strerror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strerror_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strerror_r.c

Read completely: 166 lines.

Implements `_strerror_lr()` and `strerror_r()`. It copies known `sys_errlist` entries or formats unknown errors as `"Unknown error: %d"`, returning `EINVAL` for unknown numbers and `ERANGE` if the caller buffer is too small.

With NLS enabled, localized error lists and prefixes are lazily loaded into locale caches using atomic compare-and-swap and memory barriers. The function preserves the caller's `errno`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strerror_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strerror_ss.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strerror_ss.c

Read completely: 63 lines.

Implements stack-smashing-safe `strerror_r_ss()` and `strerror_ss()`. It uses `strlcpy` for known `sys_errlist` entries and `snprintf_ss` for unknown errors, with `strerror_ss()` returning a static 64-byte buffer.

The condition `if (num >= 0 || num < sys_nerr)` appears wrong: it should almost certainly be `&&`, because the current `||` permits negative indexes and any nonnegative out-of-range number into `sys_errlist[num]`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strerror_ss.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/stresep.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/stresep.c

Read completely: 98 lines.

Implements `stresep()`, an escaped variant of `strsep()`. It returns possibly empty tokens separated by any delimiter, mutates the input by writing NULs, and if `esc` is nonzero removes escape characters by `memmove()` so escaped delimiter characters are ignored.

The caller's `*stringp` is advanced past the delimiter or set to NULL at end.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/stresep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strmode.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strmode.c

Read completely: 182 lines.

Implements `strmode()` when unavailable. It converts a `mode_t` file type and permissions into the traditional 10-character ls-style mode string plus trailing ACL placeholder space and NUL.

It handles directories, char/block devices, regular files, symlinks, sockets, fifos, whiteouts, doors when defined, setuid/setgid/sticky bits, and optional archive mode bits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strmode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strndup.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strndup.c

Read completely: 74 lines.

Implements `strndup()` when unavailable. It scans up to `n` bytes or NUL, allocates `len + 1`, copies the bounded prefix, appends NUL, and returns the new buffer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strndup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strnstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strnstr.c

Read completely: 71 lines.

Implements `strnstr()`, searching for `find` within the first `slen` characters of `s`. It handles an empty needle by returning `s`, otherwise scans for the first character and verifies the remainder with `strncmp()` without exceeding the length bound.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strnstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strsignal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strsignal.c

Read completely: 56 lines.

Implements public `strsignal(int sig)`. It uses a static `NL_TEXTMAX` buffer and delegates to `__strsignal()`, returning the resulting string pointer.

The static buffer makes unknown/realtime formatted results non-thread-safe.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strsignal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strtok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strtok.c

Read completely: 50 lines.

Implements `strtok()` as a wrapper around `strtok_r()` with a static saved pointer. This preserves traditional stateful behavior and is not thread-safe across concurrent tokenizations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strtok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strtok_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strtok_r.c

Read completely: 99 lines.

Implements reentrant `strtok_r()`. It skips leading delimiters, returns the next token, replaces the terminating delimiter with NUL, and stores continuation state in the caller-provided `lasts`.

The delimiter set can vary between calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strtok_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strxfrm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strxfrm.c

Read completely: 85 lines.

Implements `strxfrm()` and `strxfrm_l()`. Since LC_COLLATE is not implemented, transformation is a bounded copy of `src` to `dst` and the function returns `strlen(src)`.

The locale argument is ignored.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/strxfrm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/swab.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/swab.c

Read completely: 70 lines.

Implements `swab()`. It swaps adjacent byte pairs from source to destination for `nbytes / 2` pairs and ignores a trailing odd byte.

Although POSIX leaves overlapping behavior undefined, this implementation intentionally supports `src == dst` by loading both bytes before storing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/swab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscasecmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscasecmp.c

Read completely: 59 lines.

Implements `wcscasecmp()` and `wcscasecmp_l()`. It lowercases each wide character with `towlower_l()`, compares differences, and stops at the first difference or terminating NUL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscasecmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscat.c

Read completely: 58 lines.

Implements `wcscat()`. It scans to the destination terminator, copies the source wide string, appends NUL, and returns the original destination.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcschr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcschr.c

Read completely: 53 lines.

Implements `wcschr()`. It scans a wide string until it finds the requested wide character or reaches NUL, returning a cast-away-const pointer or NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcschr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscmp.c

Read completely: 63 lines.

Implements `wcscmp()`. It compares wide strings element by element until a difference or NUL, then subtracts values through `__nbrune_t`, with a comment noting it assumes `wchar_t = int`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscpy.c

Read completely: 50 lines.

Implements `wcscpy()`. It copies a NUL-terminated wide string from source to destination and returns the original destination pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscspn.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscspn.c

Read completely: 76 lines.

Implements `wcscspn()`, returning the length of the initial segment containing no characters from `set`. It fast-paths empty and single-character sets, then uses the bloom helper to reduce full set scans for larger reject sets.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscspn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscspn_bloom.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscspn_bloom.h

Read completely: 86 lines.

Provides inline bloom-filter helpers shared by wide-character span/search functions. It defines a 64-byte bloom array, two hash functions, an initializer that sets two bits per charset character, and a membership test with false positives but no false negatives.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcscspn_bloom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsdup.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsdup.c

Read completely: 44 lines.

Implements `wcsdup()`. It computes the wide-string length plus terminator, allocates with `reallocarr()` for overflow-safe sizing, and copies with `wmemcpy()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsdup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcslcat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcslcat.c

Read completely: 76 lines.

Implements `wcslcat()`, the wide-character analogue of `strlcat()`. It appends as much of `src` as fits in the full destination buffer size, NUL-terminates when size permits, and returns initial destination length plus source length for truncation detection.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcslcat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcslcpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcslcpy.c

Read completely: 72 lines.

Implements `wcslcpy()`, the wide-character analogue of `strlcpy()`. It copies up to `siz - 1` wide characters, NUL-terminates if possible, walks the rest of the source on truncation, and returns source length.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcslcpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcslen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcslen.c

Read completely: 51 lines.

Implements `wcslen()`. It advances to the terminating wide NUL and returns the pointer difference from the original string.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcslen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsncasecmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsncasecmp.c

Read completely: 61 lines.

Implements `wcsncasecmp()` and `wcsncasecmp_l()`. It compares at most `n` wide characters after locale-aware lowercasing, returning the first difference or zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsncasecmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsncat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsncat.c

Read completely: 60 lines.

Implements `wcsncat()`. It scans to the destination terminator, copies up to `n` source wide characters or until source NUL, appends NUL, and returns destination.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsncat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsncmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsncmp.c

Read completely: 64 lines.

Implements `wcsncmp()`. It compares up to `n` wide characters, returning zero for equal prefixes or the difference through `__nbrune_t` on the first mismatch.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsncmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsncpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsncpy.c

Read completely: 58 lines.

Implements `wcsncpy()`. It copies up to `n` source wide characters and pads remaining destination slots with wide NULs after an early terminator.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsncpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsnlen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsnlen.c

Read completely: 51 lines.

Implements `wcsnlen()`. It scans at most `maxlen` wide characters and returns the count before NUL or the limit.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsnlen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcspbrk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcspbrk.c

Read completely: 70 lines.

Implements `wcspbrk()`. It returns the first wide character in `s` that appears in `set`, with fast paths for empty and single-character sets and the shared bloom filter for larger sets.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcspbrk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsrchr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsrchr.c

Read completely: 55 lines.

Implements `wcsrchr()`. It first scans to the terminating NUL, then walks backward through the string to find the last occurrence of the requested wide character.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsrchr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsspn.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsspn.c

Read completely: 56 lines.

Implements `wcsspn()`. It returns the length of the initial segment of `s` consisting only of characters from `set`, using a direct nested scan.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsspn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsstr.c

Read completely: 74 lines.

Implements `wcsstr()` and, under `WCSWCS`, `wcswcs()`. It handles an empty needle, rejects when the haystack is shorter than the needle, then performs a straightforward nested wide-character substring search.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcsstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcstok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcstok.c

Read completely: 102 lines.

Implements `wcstok()`, the reentrant wide-character tokenizer. It skips leading delimiters, returns the next token, writes wide NUL over the delimiter, and stores continuation state in the caller's `last` pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcstok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcswcs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcswcs.c

Read completely: 4 lines.

Compatibility wrapper for `wcswcs()`. It defines `WCSWCS` and includes `wcsstr.c`, reusing the same implementation under the historical function name.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wcswcs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemchr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemchr.c

Read completely: 52 lines.

Implements `wmemchr()`. It scans `n` wide characters for `c` and returns the first matching position or NULL.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemchr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemcmp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemcmp.c

Read completely: 58 lines.

Implements `wmemcmp()`. It compares `n` wide characters and returns `1`, `-1`, or `0`, using `__nbrune_t` casts to avoid unsigned `wchar_t` ordering issues.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemcmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemcpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemcpy.c

Read completely: 48 lines.

Implements `wmemcpy()` by delegating to `memcpy(d, s, n * sizeof(wchar_t))` and returning the destination as `wchar_t *`. It has the same non-overlap expectation as `memcpy()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemcpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemmove.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemmove.c

Read completely: 48 lines.

Implements `wmemmove()` by delegating to `memmove(d, s, n * sizeof(wchar_t))`, preserving overlap-safe behavior for wide-character arrays.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemmove.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmempcpy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmempcpy.c

Read completely: 39 lines.

Implements `wmempcpy()`. It calls `wmemcpy(dst, src, len)` and returns the pointer just past the copied wide-character range.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmempcpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemset.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemset.c

Read completely: 53 lines.

Implements `wmemset()`. It writes wide character `c` into `n` consecutive elements and returns the original destination pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/string/wmemset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___clone.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___clone.c

Read completely: 15 lines.

Lint stub for internal `__clone()`. It declares the sched-style clone signature and returns `0` for lint/interface checking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___clone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___sigaction_siginfo.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___sigaction_siginfo.c

Read completely: 11 lines.

Lint stub for `__sigaction_siginfo()`. It declares the signal-action compatibility interface and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___sigaction_siginfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___syscall.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___syscall.c

Read completely: 16 lines.

Lint stub for variadic `__syscall()`. It declares a `quad_t` first argument and varargs, returning `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___vfork14.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___vfork14.c

Read completely: 16 lines.

Lint stub for compatibility symbol `__vfork14()`. It enables `__LIBC12_SOURCE__`, includes compatibility `unistd.h`, and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint___vfork14.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_brk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_brk.c

Read completely: 15 lines.

Lint stub for `brk()`. It declares the heap-break interface and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_brk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_clone.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_clone.c

Read completely: 16 lines.

Lint stub for public `clone()`. It defines `_GNU_SOURCE`, includes `<sched.h>`, declares the clone-style signature, and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_clone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_getcontext.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_getcontext.c

Read completely: 15 lines.

Lint stub for `getcontext()`. It declares the `ucontext_t *` interface and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_getcontext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_pipe.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_pipe.c

Read completely: 15 lines.

Lint stub for `pipe()`. It declares the two-file-descriptor array interface and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_ptrace.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_ptrace.c

Read completely: 17 lines.

Lint stub for `ptrace()`. It includes signal/types/ptrace headers for the correct signature and returns `0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_ptrace.c -->