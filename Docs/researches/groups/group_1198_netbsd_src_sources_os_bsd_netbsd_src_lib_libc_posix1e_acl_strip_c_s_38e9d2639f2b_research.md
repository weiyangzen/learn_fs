# Group Research: group_1198_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_posix1e_acl_strip_c_s_38e9d2639f2b

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_strip.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_strip.c

Implements `acl_strip_np()` and `acl_is_trivial_np()` for POSIX.1e and NFSv4 ACLs. POSIX ACL stripping keeps only `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, and `ACL_OTHER`, optionally recalculating `ACL_MASK` if a mask existed. NFSv4 stripping derives mode bits from the ACL with `__acl_nfs4_sync_mode_from_acl()` and rebuilds a trivial ACL with `__acl_nfs4_trivial_from_mode_libc()`.

Key dependencies are brand helpers from `acl_support.h`, public ACL iteration/copy APIs, `acl_calc_mask()`, and kernel/shared NFSv4 ACL helpers declared in `sys/acl.h`. `acl_is_trivial_np()` treats a POSIX ACL with exactly three entries as trivial and compares NFSv4 ACLs against both normal and canonical-six trivial forms via `_acl_differs()`.

Important behavior: invalid or unknown ACL brands return `EINVAL`; allocation failures return `NULL`, sometimes with `ENOMEM`. The POSIX strip helper duplicates the input first, then creates a new ACL, so input ACL ordering and entry brands are expected to be valid.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_strip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support.c

Provides internal support routines for POSIX.1e ACL handling. It includes ACL comparison, POSIX entry sorting, POSIX validity checks, permission string conversion, raw entry insertion, old ACL type translation, and whitespace helpers.

Important functions:
- `_acl_differs()` compares brand-compatible ACLs entry-by-entry, including tag, id, permissions, entry type, and flags.
- `_posix1e_acl_sort()` sorts ACL entries into kernel validation order.
- `_posix1e_acl_check()` validates sorted POSIX ACLs: permission bits, tag order, required single owner/group/other entries, optional single mask, and monotonically increasing named user/group ids.
- `_posix1e_acl_perm_to_string()` and `_posix1e_acl_string_to_perm()` convert between `rwx` text and permission bits.
- `_acl_type_unold()` maps legacy access/default ACL type constants to current constants.

The file mirrors kernel ACL validation expectations for userland preflight. It relies on `_acl_brand()` and `_entry_brand()` being meaningful, and uses `assert()` heavily for internal invariants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support.h

Internal header for libc POSIX.1e/NFSv4 ACL support. It declares shared helpers for ACL branding, validation, formatting, parsing, name/id conversion, NFSv4 text conversion, POSIX permission conversion, and whitespace trimming.

This header is the coordination point between `acl_strip.c`, `acl_support.c`, `acl_support_nfs4.c`, `acl_to_text.c`, `acl_to_text_nfs4.c`, `acl_valid.c`, and other ACL source files in the same directory. It also defines `_POSIX1E_ACL_STRING_PERM_MAXSIZE` as `3` for `rwx` text buffers.

Because these declarations are internal to libc, they expose implementation details such as ACL brand state and text parser heuristics rather than public API contracts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support_nfs4.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support_nfs4.c

Provides NFSv4 ACL flag and access-mask formatting/parsing helpers. It maps bit values to verbose names and compact one-character forms for inheritance/audit flags and NFSv4 access permissions.

Important functions:
- `_nfs4_format_flags()` and `_nfs4_format_access_mask()` output either verbose slash-separated names or compact character fields.
- `_nfs4_parse_flags()` and `_nfs4_parse_access_mask()` first try verbose parsing and fall back to compact parsing if no verbose token matched.
- Shared static helpers implement flag scanning and parse diagnostics.

The access-mask table includes individual permissions plus aggregate set constants such as `ACL_FULL_SET`, `ACL_MODIFY_SET`, `ACL_READ_SET`, and `ACL_WRITE_SET`. Parse errors use `warnx()` with field-specific messages and return `-1`, while parsed bitsets are still assigned through output parameters.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support_nfs4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_to_text.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_to_text.c

Implements `acl_to_text()` and `acl_to_text_np()`. It dispatches by ACL brand: POSIX ACLs are formatted locally, NFSv4 ACLs are delegated to `_nfs4_acl_to_text_np()`.

The POSIX formatter emits lines such as `user::rwx`, `user:name:r--`, `group::r-x`, `mask::r--`, and `other::---`. It computes effective permissions for named users, group owner, and named groups by applying the mask when present, adding `# effective:` comments when the effective bits differ.

Dependencies include `_posix1e_acl_perm_to_string()`, `_posix1e_acl_id_to_name()`, `acl_support.h`, `asprintf()`, and ACL brand detection. Unknown tags or bad brands return `EINVAL`. The implementation repeatedly rebuilds the output string with `asprintf()`, favoring simplicity over allocation efficiency.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_to_text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_to_text_nfs4.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_to_text_nfs4.c

Formats NFSv4 ACLs into text. Each entry is rendered as who, access mask, flags, entry type, and optionally numeric id suffix. The formatter supports owner/group/everyone special principals and named users/groups.

Important helpers:
- `format_who()` maps ACL tags to `owner@`, `group@`, `everyone@`, `user:<name|id>`, or `group:<name|id>`.
- `format_entry_type()` maps allow/deny/audit/alarm entry types.
- `format_entry()` combines principal, `_nfs4_format_access_mask()`, `_nfs4_format_flags()`, and type.
- `_nfs4_acl_to_text_np()` iterates entries and returns a malloced string.

Flags include `ACL_TEXT_NUMERIC_IDS`, `ACL_TEXT_VERBOSE`, and `ACL_TEXT_APPEND_ID`. Name lookup uses `getpwuid()`/`getgrgid()` and is explicitly noted as thread-unsafe. Formatting assumes each entry fits within `MAX_ENTRY_LENGTH` and asserts against truncation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_to_text_nfs4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_valid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_valid.c

Implements ACL validation entry points. `acl_valid()` validates POSIX ACL structure in userland by sorting and calling `_posix1e_acl_check()`. `acl_valid_file_np()`, `acl_valid_link_np()`, and `acl_valid_fd_np()` call kernel ACL check syscalls for a path, link, or fd after normalizing legacy ACL type constants.

For POSIX ACL types (`ACL_TYPE_ACCESS` or `ACL_TYPE_DEFAULT`), the file/link/fd variants sort before checking. The fd variant resets `ats_cur_entry` before the syscall. Invalid null arguments return `EINVAL`.

This file bridges pure userland POSIX structural validation and target-aware kernel validation, so it is important for callers that need filesystem-specific ACL acceptability.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_valid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/Makefile.inc

Build fragment adding quad support routines to libc. It includes comparison, division, modulo, multiplication, negation, shifts, and integer/floating conversion helpers.

The selected source set is architecture-sensitive. Generic conversion files are skipped for earm architectures, which instead use IEEE-754-specific conversion implementations plus C shift helpers. m68k/m68000 select assembly shift routines. The file also adds older bitwise/add/sub helpers with a comment noting they appear unused.

This Makefile is the build switchboard for compiler runtime-style 64-bit arithmetic support inside libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/Makefile

Simple historical test Makefile building two interactive test programs: `mul` from `mul.c` plus `../muldi3.c`, and `divrem` from `divrem.c` plus `../qdivrem.c`.

It invokes `gcc -g -DSPARC_XXX` directly and is not integrated with modern NetBSD ATF test infrastructure. Its purpose is manual/local validation of quad multiplication and division/reminder helper behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/divrem.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/divrem.c

Interactive test driver for `__qdivrem()`. It reads two 64-bit values as high/low 32-bit words in decimal or hex, calls `__qdivrem()` to compute quotient and remainder, and prints both word-pair and concatenated hex results.

The program uses old-style K&R `main()` and calls `exit(0)` without including `<stdlib.h>`, reflecting its historical/manual-test nature. It assumes the union layout of `long long` and two `unsigned int` words matches the target’s expected display order.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/divrem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/mul.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/mul.c

Interactive test driver for `__muldi3()`. It reads two 64-bit values as high/low 32-bit words in decimal or hex, invokes the quad multiply helper, and prints the product.

Like `divrem.c`, this is a historical manual diagnostic program with old-style `main()` and target-layout assumptions. It is useful for spot-checking the low-level multiplication routine but not a portable automated test.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixdfdi.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixdfdi.c

Implements `__fixdfdi(double)`, converting `double` to signed 64-bit `quad_t`. It clamps values below `QUAD_MIN` and above `QUAD_MAX`, and otherwise casts through `u_quad_t`, handling negative values by negating after unsigned conversion.

This is the generic conversion implementation used where direct floating conversion is acceptable. It includes softfloat glue for `SOFTFLOAT` or ARM EABI builds, then relies on `quad.h` constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixdfdi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixdfdi_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixdfdi_ieee754.c

IEEE-754-specific `double` to signed `quad_t` conversion. It unpacks `union ieee_double_u`, derives exponent and sign, builds the integer from the implicit bit plus high/low fraction fields, shifts according to exponent, and applies sign.

Out-of-range exponents clamp to `QUAD_MIN` or `QUAD_MAX`. Unlike the generic version, this avoids relying on compiler/runtime double-to-64-bit casts, which is important on architectures needing these helpers to implement those casts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixdfdi_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixsfdi.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixsfdi.c

Generic `float` to signed `quad_t` conversion via `__fixsfdi(float)`. It mirrors `fixdfdi.c`: clamp below `QUAD_MIN`, clamp above `QUAD_MAX`, and otherwise cast through `u_quad_t`, with special handling for negative values.

It is portable but depends on the compiler being able to perform the underlying floating-to-integer conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixsfdi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixsfdi_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixsfdi_ieee754.c

IEEE-754-specific `float` to signed `quad_t` conversion. It unpacks `union ieee_single_u`, handles negative/positive sign, returns zero for exponent below zero, clamps exponent above 62, and shifts the implicit-bit-plus-fraction integer into place.

This provides a cast implementation that does not recursively depend on compiler-provided 64-bit conversion support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixsfdi_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixunsdfdi.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixunsdfdi.c

Generic `double` to unsigned `u_quad_t` conversion via `__fixunsdfdi(double)`. Negative inputs return `UQUAD_MAX` per this historical helper’s semantics. Inputs at or above `2^64 - 1` also return `UQUAD_MAX`.

For in-range values, it divides by `2^32` to form the high word and subtracts to form the low word in a `union uu`. Comments call out old GCC issues and rounding assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixunsdfdi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixunsdfdi_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixunsdfdi_ieee754.c

IEEE-754-specific `double` to unsigned `u_quad_t` conversion. It unpacks sign, exponent, and fraction fields directly. Negative inputs and exponent values above 63 return `UQUAD_MAX`; negative exponents return zero.

The conversion assembles the implicit bit, high fraction, and low fraction into a 64-bit unsigned result with right or left shifts based on exponent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixunsdfdi_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixunssfdi.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixunssfdi.c

Generic `float` to unsigned `u_quad_t` conversion. It promotes the float to double for arithmetic, maps negative and out-of-range values to `UQUAD_MAX`, estimates the high 32-bit part, then adjusts for rounding drift before assigning the low word.

This implementation is defensive around floating rounding and old compiler behavior. It shares historical semantics with the other unsigned conversion helpers: negative does not become zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixunssfdi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixunssfdi_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixunssfdi_ieee754.c

IEEE-754-specific `float` to unsigned `u_quad_t` conversion. It unpacks `union ieee_single_u`, returns `UQUAD_MAX` for negative or exponent-above-63 values, returns zero for exponent below zero, and otherwise shifts the implicit bit plus single-precision fraction.

This is the ARM/IEEE path avoiding dependency on compiler-emitted cast helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/fixunssfdi_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatdidf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatdidf.c

Generic signed `quad_t` to `double` conversion via `__floatdidf()`. It records sign, converts the magnitude to a `union uu`, computes `high * 2^32 + low` in double, and reapplies the sign.

This is portable code that does not inspect floating-point representation, but it may be less efficient than architecture-specific or IEEE-aware implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatdidf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatdidf_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatdidf_ieee754.c

IEEE-754-specific signed `quad_t` to `double` conversion. It handles `0`, `1`, and `QUAD_MIN` specially, then uses `__builtin_clzll()` to normalize the integer, fills double fraction high/low fields, sets exponent bias, and returns the constructed double.

It directly creates the IEEE representation, avoiding intermediate floating arithmetic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatdidf_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatdisf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatdisf.c

Generic signed `quad_t` to `float` conversion via `__floatdisf()`. It splits the magnitude into high/low words, computes the value using double arithmetic, assigns to float, and reapplies sign.

The code comments note that using double is conservative. It is portable and representation-agnostic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatdisf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatdisf_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatdisf_ieee754.c

IEEE-754-specific signed `quad_t` to `float` conversion. It handles zero, one, and `QUAD_MIN`, then normalizes the magnitude and fills an IEEE single union.

On LP64 or MIPS n32 it uses `__builtin_clzll()`. On 32-bit paths it inspects the high and low halves manually to compute the leading-zero count and fraction. It does not implement explicit rounding beyond truncating fraction bits into the target representation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatdisf_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatundidf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatundidf.c

Generic unsigned `u_quad_t` to `double` conversion. It splits the integer into high and low words and computes `high * 2^32 + low`.

This is the unsigned analogue of `floatdidf.c`, without sign handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatundidf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatundidf_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatundidf_ieee754.c

IEEE-754-specific unsigned `u_quad_t` to `double` conversion. It returns zero for zero, normalizes the integer with `__builtin_clzll()`, fills double fraction fields, and sets the biased exponent.

This constructs the destination double directly rather than using floating arithmetic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatundidf_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatundisf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatundisf.c

Generic unsigned `u_quad_t` to `float` conversion. It uses the same high-word times `2^32` plus low-word pattern as the double variant, with double arithmetic used before returning a float.

This is simple and portable, relying on normal compiler floating conversion behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatundisf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatundisf_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatundisf_ieee754.c

IEEE-754-specific unsigned `u_quad_t` to `float` conversion. It handles zero and one, computes the leading set bit, fills the single-precision fraction field, and sets the exponent.

The implementation has separate LP64 and 32-bit code paths, matching `floatdisf_ieee754.c` without sign handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatundisf_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatunditf_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatunditf_ieee754.c

Converts unsigned `u_quad_t` to `long double` using IEEE extended representation. It rejects VAX because VAX lacks a distinct long double format. The active implementation normalizes the 64-bit integer, fills `union ieee_ext_u` exponent and fraction fields, and returns `extu_ld`.

The file contains an inactive portable arithmetic version under `#if 0`. The active path supports optional middle fraction fields via `EXT_FRACHMBITS` and `EXT_FRACLMBITS`, adapting to platform extended-precision layouts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/quad/floatunditf_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/Makefile.inc

Build fragment for libc regex sources. It adds `regcomp.c`, `regerror.c`, `regexec.c`, `regfree.c`, and `regsub.c`, sets `.PATH` to the regex directory, defines `POSIX_MISTAKE`, and installs regex manual links.

`POSIX_MISTAKE` affects parser behavior around unmatched `)` in EREs, preserving historical POSIX compatibility noted in `regcomp.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/cname.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/cname.h

Static table mapping POSIX collating element names to single character codes. It includes control names (`NUL`, `SOH`, `ESC`, etc.), common aliases (`alert`, `tab`, `newline`), punctuation names, digit names, and delimiter variants.

Used by `regcomp.c` when parsing bracket collating elements like `[.name.]` and equivalence classes. The table only maps single-character elements; unknown multi-character names are rejected unless they are a single multibyte character in NLS mode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/cname.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/engine.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/engine.c

Core regex execution engine included multiple times by `regexec.c` with different state-set and character conversion macros. It implements matching over the compiled strip representation from `regex2.h`.

Major functions:
- `matcher()` sets up bounds, optional `REG_STARTEND`, Boyer-Moore “must” prescreening, and submatch/backreference handling.
- `walk()` runs the NFA state propagation across the subject and tracks possible match endpoints.
- `step()` transitions state sets through strip operators.
- `dissect()` reconstructs submatch boundaries for regexes without backreferences.
- `backref()` recursively validates matches requiring backreference equality and captures.
- `stepback()` helps adjust start positions for must-string offsets, including multibyte-aware stepping under NLS.

The engine supports anchors, BOS/EOS, word boundaries, non-word boundaries, bracket sets, alternation, plus/question loops, and backreferences. Backreferences use recursion with `MAX_RECURSION` guard for empty references. Debug printing is compiled only under `REDEBUG`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/engine.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regcomp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regcomp.c

Regex compiler for Henry Spencer-style POSIX regexes with NetBSD/FreeBSD updates, GNU extension support, wide-character handling, and Boyer-Moore optimization metadata.

Important responsibilities:
- `regcomp_internal()` allocates parse/guts state, chooses BRE vs ERE parser, emits the strip, compacts it, finds mandatory literals, computes jump tables, counts plus nesting, and populates `regex_t`.
- `p_ere_exp()`, `p_simp_re()`, and `p_re()` parse ERE/BRE atoms, concatenation, branches, anchors, groups, backreferences, and repetitions.
- Bracket parsing supports character classes, equivalence classes, collating symbols, ranges, case-insensitive sets, word-boundary special cases `[[:<:]]` and `[[:>:]]`, and GNU pseudo-classes `\w`, `\W`, `\s`, `\S`.
- `repeat()` lowers bounded repetition into strip operations by duplication and optional/plus constructs.
- `findmust()`, `computejumps()`, and `computematchjumps()` derive literal substrings and Boyer-Moore skip tables for `regexec()`.
- `allocset()`, `CHadd()`, `CHaddrange()`, and `CHaddtype()` build cset data for `OANYOF`.

The compiled representation is a strip of `sop` operators. The file is careful about allocation growth with `reallocarray()`, large pattern size overflow, and preserving the first parse error. It uses `REG_GNU` when enabled and `PFLAG_LEGACY_ESC` internally for escape behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regcomp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regerror.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regerror.c

Implements `regerror()`, mapping regex error codes to human-readable messages or symbolic names. It supports NetBSD extensions `REG_ATOI` and `REG_ITOA` for converting between names and numbers.

The static `rerrs[]` table covers standard errors such as `REG_NOMATCH`, `REG_BADPAT`, `REG_EBRACK`, `REG_ESPACE`, `REG_INVARG`, and `REG_ILLSEQ`. `regerror()` returns the required buffer length including NUL and copies with `strlcpy()` when a destination buffer is supplied.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regerror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regex2.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regex2.h

Internal regex representation header. It defines magic values, strip operator encoding, all regex opcodes, character-set representation, `CHIN()` membership helpers, and `struct re_guts`.

Key concepts:
- A compiled regex is a strip of `sop` operators with opcode and operand packed into 32 bits.
- Operators include characters, anchors, any, character sets, backrefs, repetition delimiters, parentheses, alternation, BOS/EOS, and word boundaries.
- `cset` stores bitmap entries for small chars plus wide chars, ranges, character classes, inversion, and case-insensitive behavior.
- `struct re_guts` stores the strip, csets, flags, state counts, optimization literal (`must`), Boyer-Moore jump tables, subexpression count, backreference marker, and plus nesting depth.

This header is consumed by both compiler and executor and is not public ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regex2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regexec.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regexec.c

Public `regexec()` wrapper and engine generator. It includes `engine.c` three times with different macro sets:
- small state bitset matcher for regexes fitting in a machine `long`,
- large byte-array state matcher,
- multibyte-aware matcher.

`regexec()` validates magic values, filters execution flags, and dispatches to `mmatcher()` when `MB_CUR_MAX > 1`, otherwise to `smatcher()` when state count fits and `REG_LARGE` is not requested, else to `lmatcher()`.

It provides `xmbrtowc()` wrappers that treat invalid multibyte sequences as one dummy character for matching progress, resetting conversion state after errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regexec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regfree.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regfree.c

Implements `regfree()`. It validates regex magic, marks both public and guts structures invalid, and frees all compiler allocations: strip, cset ranges/wides/types, cset array, mandatory literal string, Boyer-Moore jump tables, and `re_guts`.

A notable detail is freeing `charjump` with `free(&g->charjump[CHAR_MIN])` because `regcomp.c` shifts the stored pointer to allow signed-char indexing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regfree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regsub.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regsub.c

Implements replacement expansion helpers `regnsub()` and `regasub()`. The shared `regsub1()` expands `&` as match 0 and `\digit` as submatch references, while allowing escaped `\\` and `\&`.

The internal `struct str` supports either fixed caller buffers or dynamically allocated buffers. If fixed space is insufficient, it still counts required length but omits writes. `regasub()` allocates and grows the output buffer in `REINCR` chunks.

Return value is the expanded length excluding the terminating NUL; `-1` signals allocation or fixed-buffer failure conditions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/regsub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/utils.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/utils.h

Utility header for regex internals. It abstracts wide-character support under `NLS`; without NLS it defines lightweight stand-ins for `wint_t`, `mbstate_t`, `wctype_t`, wide case/class functions, and declares local `__regex_wctype()` / `__regex_iswctype()`.

It defines duplication limits, character-domain constants (`NC_MAX`, `NC`), unsigned character typedef `uch`, assertion behavior tied to `REDEBUG`, and a compatibility mapping from `memmove()` to `bcopy()` under `USEBCOPY`.

This header keeps the regex implementation buildable in libc and host-tool contexts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/regex/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/Makefile.inc

Build fragment for resolver sources in libc. It sets `.PATH`, defines `COMPAT__RES` and `USE_POLL`, and adds resolver files such as `h_errno.c`, `herror.c`, `res_comp.c`, `res_data.c`, `res_init.c`, `res_query.c`, `res_send.c`, `res_state.c`, and `mtctxres.c`.

It also includes `res_compat.c` specifically for `COMPAT__RES`, and suppresses a string overflow warning for `res_query.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/h_errno.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/h_errno.c

Provides accessors for resolver host error state. `__h_errno()` returns the address of `_nres.res_h_errno`. `__h_errno_set()` writes both the global `h_errno` compatibility symbol and the supplied resolver state’s `res_h_errno`.

This file bridges old global `h_errno` behavior with resolver-state-based error storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/h_errno.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/herror.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/herror.c

Implements legacy host lookup error reporting. It defines `h_errlist[]`, `h_nerr`, optional global `h_errno`, `herror()`, and `hstrerror()`.

`herror()` writes an optional prefix, `": "`, the string for current `*__h_errno()`, and newline to standard error using `writev()`. `hstrerror()` maps negative values to “Resolver internal error”, in-range values to `h_errlist`, and others to “Unknown resolver error”.

This is compatibility API around resolver/host lookup errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/herror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/mtctxres.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/mtctxres.c

Implements legacy multi-thread resolver context support. With `DO_PTHREADS`, it creates a thread-specific data key for `mtctxres_t`, lazily initializes it if needed, allocates per-thread contexts, and frees them via a destructor. Without pthread support or on allocation/setup failure, it returns a shared static context.

`__res_enable_mt()` and `__res_disable_mt()` are kept as Solaris 8 private-interface compatibility stubs. The main exported accessor is `___mtctxres()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/mtctxres.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/res_comp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_comp.c

Resolver compatibility functions for DNS name compression, expansion, skipping, and name validity checks.

Important functions:
- `dn_expand()` wraps `ns_name_uncompress()` and converts root `"."` to empty string.
- `dn_comp()` wraps `ns_name_compress()`.
- `dn_skipname()` wraps `ns_name_skip()`.
- `res_hnok()`, `res_ownok()`, `res_mailok()`, and `res_dnok()` validate hostname-like, owner, mail, and domain names using explicit ASCII checks.

Under `BIND_4_COMPAT`, it also provides old put/get short/long wrappers over `ns_put16`, `ns_put32`, `ns_get16`, and `ns_get32`. The character checks deliberately avoid locale-sensitive ctype macros for DNS wire/presentation constraints.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/res_comp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/res_compat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_compat.c

Provides binary compatibility for the old global `_res` resolver state when `__BIND_NOSTATIC` is not defined. It defines `struct __res_state _res` with optional static initialization and exposes:
- `__res_get_old_state()` returning `_res`,
- `__res_put_old_state()` copying a newer state back into `_res`.

`res_data.c` uses these hooks under `COMPAT__RES` so programs that modified `_res` directly before `res_init()` can still influence `_nres` initialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/res_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/res_data.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_data.c

Compatibility wrapper layer exposing traditional resolver APIs over the stateful `res_n*` interfaces and global `_nres`.

Key behavior:
- `res_init()` initializes `_nres`, preserving direct `_res` compatibility fields under `COMPAT__RES`, setting defaults for retrans/retry/options/id, and calling `__res_vinit()`.
- Query/send/update wrappers lazily call `res_init()` if needed, set `NETDB_INTERNAL` on init failure where appropriate, then delegate to `res_nmkquery()`, `res_nquery()`, `res_nsend()`, `res_nsearch()`, `res_nquerydomain()`, etc.
- Debug wrappers route `p_query()`, `fp_query()`, and `fp_nquery()` through `res_pquery()`.
- Hook setters write `_nres.qhook` and `_nres.rhook`.
- Miscellaneous wrappers include `res_close()`, `res_isourserver()`, `res_opt()`, `res_randomid()`, and `hostalias()`.

This file is the main old-API facade over modern resolver state management.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/resolv/res_data.c -->