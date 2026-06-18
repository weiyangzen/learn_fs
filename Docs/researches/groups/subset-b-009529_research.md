# Research Report: subset-b-009529

This grouped report covers the requested `subset-b-009529` files under `sources/test-tools/xfstests-bld/fstests-bld`. Each section is delimited for deterministic splitting into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/pack.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/pack.c

Purpose: `pack.c` implements the private `uuid_pack()` conversion from the library's structured `struct uuid` view into the public 16-byte `uuid_t` wire/storage representation. It is part of the e2fsprogs/libuuid compatibility implementation and enforces the DCE UUID field byte order independent of host endian layout.

Important APIs, types, and functions: the only exported function in this file is `void uuid_pack(const struct uuid *uu, uuid_t ptr)`. It depends on `struct uuid` and `uuid_t` from `uuidP.h` and uses `uint32_t` temporaries for field shifts. The fields packed are `time_low`, `time_mid`, `time_hi_and_version`, `clock_seq`, and the six-byte `node`.

Control flow: `uuid_pack()` casts the output array to `unsigned char *`, then writes integer fields byte-by-byte in big-endian UUID text/network order: `time_low` into bytes 0-3, `time_mid` into 4-5, `time_hi_and_version` into 6-7, and `clock_seq` into 8-9. It copies `node` directly into bytes 10-15 with `memcpy()`.

State and persistence: the function is stateless and performs no allocation or I/O. Its only side effect is writing exactly 16 bytes to the caller-provided `uuid_t`.

Dependencies and integration points: `uuid_parse()` builds a `struct uuid` from text and calls `uuid_pack()` to produce the public binary form. UUID generators elsewhere in libuuid can also use this helper. `uuid_unpack()` in `unpack.c` is the inverse operation, and `uuid_unparse()` depends on that inverse.

Risks: callers must pass a valid output buffer of at least 16 bytes and a fully initialized `struct uuid`. The function does no null checks and silently truncates higher bits if callers put values larger than the declared field widths into the struct. The manual byte order is correct for UUID layout but should not be replaced with raw struct copies because that would be host-endian and padding-sensitive.

Test signals: `tst_uuid.c` exercises this path indirectly through `uuid_parse()`, `uuid_unparse()`, and `uuid_compare()`. Round-trip string/binary tests are the strongest signal for regressions in field order.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/pack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/parse.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/parse.c

Purpose: `parse.c` implements `uuid_parse()`, the public conversion from canonical UUID text into the 16-byte `uuid_t` representation.

Important APIs, types, and functions: `int uuid_parse(const char *in, uuid_t uu)` returns `0` on success and `-1` on invalid input. It uses `strlen()`, `isxdigit()`, `strtoul()`, and the private `uuid_pack()` helper. The intermediate representation is `struct uuid` from `uuidP.h`.

Control flow: the function first requires `strlen(in) == 36`. It then scans positions 0 through 36, requiring hyphens at offsets 8, 13, 18, and 23, a terminating NUL at offset 36, and hexadecimal digits everywhere else. After validation, it parses the five UUID text fields with `strtoul()`: 8 hex digits for `time_low`, 4 for `time_mid`, 4 for `time_hi_and_version`, 4 for `clock_seq`, and six two-digit octets for `node`. Finally it calls `uuid_pack()` to write the public 16-byte output.

State and persistence: no persistent state, allocation, or I/O. The only side effect is filling the caller's `uuid_t` on success. On invalid input, the function returns before writing a parsed UUID.

Dependencies and integration points: declared in `uuid.h.in` and documented in `uuid_parse.3.in`. It is used by `tst_uuid.c` and by the debug path in `uuid_time.c`. Its binary output must match `uuid_unparse()` formatting and `uuid_compare()` semantics.

Risks: `strlen(in)` assumes `in` is a valid NUL-terminated string; passing null or unterminated memory is unsafe. The validation loop relies on `isxdigit(*cp)` without casting to `unsigned char`, which is conventional in older C but can be undefined for negative signed-char values outside ASCII. The parser accepts upper and lower case hex but only the canonical hyphenated length and positions. The loop includes `i <= 36` and handles the terminator explicitly; this is intentional but brittle if modified.

Test signals: `tst_uuid.c` includes positive lower/upper-case UUID parse cases and invalid cases for length, misplaced hyphens, and non-hex characters. Round-tripping parsed UUIDs through `uuid_compare()` is the key integration test.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/tst_uuid.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/tst_uuid.c

Purpose: `tst_uuid.c` is a standalone smoke and regression test program for the UUID library. It validates generation, parsing, unparsing, type/variant decoding, comparison, clearing, copying, and selected invalid parse inputs.

Important APIs, types, and functions: `test_uuid()` wraps `uuid_parse()` expectations for valid or invalid strings. `main()` uses public libuuid APIs from `<uuid/uuid.h>`: `uuid_generate()`, `uuid_generate_random()`, `uuid_generate_time()`, `uuid_unparse()`, `uuid_type()`, `uuid_variant()`, `uuid_time()`, `uuid_parse()`, `uuid_compare()`, `uuid_clear()`, `uuid_is_null()`, and `uuid_copy()`. It conditionally defines GCC unused attributes and has a Windows compatibility include block.

Control flow: `main()` generates a default UUID, prints string and raw bytes, and checks the DCE variant. It repeats for random UUID generation and additionally requires type 4. It then generates a time UUID, requires DCE variant and type 1, decodes its timestamp, parses the printed string back, and compares it with the original. It clears and checks a UUID for nullness, copies and compares another UUID, and finally runs a table of canonical/invalid parse strings through `test_uuid()`. Any failure increments `failed`; nonzero failures exit with status 1.

State and persistence: the program keeps only local stack buffers and an integer failure count. It prints diagnostics to stdout/stderr and returns process status as the persistent test signal. It does not create files.

Dependencies and integration points: depends on the installed or in-tree `<uuid/uuid.h>` and the UUID library implementation. It is a build/test target signal for the libuuid subset and cross-checks implementation files in this group, including `parse.c`, `unparse.c`, `uuid_time.c`, and private pack/unpack behavior.

Risks: generated UUID expectations depend on the generation backend being available and setting correct variant/type bits. The test prints `timeval` fields with `%ld`, which matches many Unix ABIs but can be portability-sensitive. It is a smoke test, not exhaustive property testing; it does not test all variants, null input, buffer sizing, or malformed high-bit characters.

Test signals: the executable's exit code is the primary signal. The parse cases cover uppercase/lowercase acceptance, too-long and too-short strings, misplaced separators, missing separators, and non-hex characters at both ends.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/tst_uuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/unpack.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/unpack.c

Purpose: `unpack.c` implements the private inverse of `uuid_pack()`: it converts the public 16-byte `uuid_t` representation into a structured `struct uuid`.

Important APIs, types, and functions: the file exports `void uuid_unpack(const uuid_t in, struct uuid *uu)`. It uses `uint8_t`, `uint32_t`, `memcpy()`, and `struct uuid` from `uuidP.h`.

Control flow: the function walks the input byte array with a pointer. It accumulates bytes into integer fields using left shifts and ORs: bytes 0-3 become `time_low`, 4-5 `time_mid`, 6-7 `time_hi_and_version`, and 8-9 `clock_seq`. It copies bytes 10-15 into `node`.

State and persistence: no state beyond the caller-provided output struct. It performs no allocation or I/O and has no persistence.

Dependencies and integration points: `uuid_unparse()` calls `uuid_unpack()` before formatting. `uuid_time()`, `uuid_type()`, and `uuid_variant()` call it to inspect UUID internals. The byte order must remain synchronized with `uuid_pack()`.

Risks: no null or size checks are performed; callers must provide a valid 16-byte input and writable struct. The manual decode is endian-stable. Any field order mistake would corrupt formatted UUIDs and timestamp/variant extraction.

Test signals: `tst_uuid.c` exercises this through unparse, compare after parse/unparse, type/variant checks, and time extraction. A good regression test is a known UUID byte array with expected textual form and timestamp fields.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/unpack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/unparse.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/unparse.c

Purpose: `unparse.c` converts a binary `uuid_t` into canonical hyphenated UUID text in lower-case, upper-case, or build-configured default case.

Important APIs, types, and functions: public functions are `uuid_unparse()`, `uuid_unparse_lower()`, and `uuid_unparse_upper()`. The internal `uuid_unparse_x()` unpacks the UUID and formats using either `fmt_lower` or `fmt_upper`. It depends on `uuid_unpack()` and `struct uuid`.

Control flow: `uuid_unparse_x()` calls `uuid_unpack()` and then writes to the caller's `out` buffer using `sprintf()` with the format `%08x-%04x-%04x-%02x%02x-%02x...`. The `clock_seq` field is split into two bytes for the fourth UUID group, and the six node bytes form the final group. The default `uuid_unparse()` chooses upper case only when `UUID_UNPARSE_DEFAULT_UPPER` is defined; otherwise it uses lower case.

State and persistence: stateless; it only writes formatted text to the caller's buffer. The caller must provide enough space for 36 characters plus NUL.

Dependencies and integration points: declared in `uuid.h.in`, documented in `uuid_unparse.3.in`, and used by `tst_uuid.c`. Its output is accepted by `uuid_parse()` and is usually the user-facing representation of generated UUIDs.

Risks: uses `sprintf()` rather than bounded formatting, so the API contract requires a sufficiently large output buffer. Any change to format width, hyphen placement, or case default can affect ABI/user expectations. It assumes `uuid_unpack()` returns fields normalized to integer values.

Test signals: `tst_uuid.c` prints generated UUID strings and parses a generated time UUID back for comparison. Additional stable tests should validate known byte arrays against exact lower and upper strings.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/unparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.3.in

Purpose: this manpage template is the overview documentation for the DCE-compatible UUID library shipped with e2fsprogs.

Important APIs, types, and functions: it introduces `<uuid/uuid.h>` and links readers to `uuid_clear(3)`, `uuid_compare(3)`, `uuid_copy(3)`, `uuid_generate(3)`, `uuid_is_null(3)`, `uuid_parse(3)`, `uuid_time(3)`, and `uuid_unparse(3)`.

Control flow: as documentation, there is no executable control flow. The template uses Autoconf/e2fsprogs substitutions in `.TH`, including `@E2FSPROGS_MONTH@`, `@E2FSPROGS_YEAR@`, and `@E2FSPROGS_VERSION@`.

State and persistence: installed as a section 3 manpage after substitution. It does not mutate state but becomes part of the installed API documentation.

Dependencies and integration points: generated by the e2fsprogs build substitution tooling, likely via `util/subst` and `subst.conf.in`. It must stay consistent with `uuid.h.in` and implementation behavior.

Risks: the uniqueness and DCE compatibility claims are user-facing. If generation defaults or entropy behavior changes, this overview must be updated with `uuid_generate.3.in`. The availability URL is historical.

Test signals: documentation tests are substitution/build installation checks and manual consistency review against the public header and manpage cross-references.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.h.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.h.in

Purpose: `uuid.h.in` is the public libuuid header template. It defines the ABI-facing `uuid_t` type, variant/type constants, and function prototypes.

Important APIs, types, and functions: `typedef unsigned char uuid_t[16]`; variant constants `UUID_VARIANT_NCS`, `UUID_VARIANT_DCE`, `UUID_VARIANT_MICROSOFT`, and `UUID_VARIANT_OTHER`; type constants `UUID_TYPE_DCE_TIME` and `UUID_TYPE_DCE_RANDOM`; macro `UUID_DEFINE()`; public functions for clear, compare, copy, generate, is-null, parse, unparse, time, type, and variant.

Control flow: no runtime control flow. Preprocessor flow handles `_WIN32` time includes, C++ `extern "C"`, and GCC-specific `__attribute__((unused))` for `UUID_DEFINE()`.

State and persistence: this header persists as the installed public contract. It declares functions that mutate caller-provided UUID buffers but owns no state itself.

Dependencies and integration points: included by clients as `<uuid/uuid.h>` and by private `uuidP.h`. It requires system types and time headers. Manpages in this group document the prototypes declared here. Implementations in `pack.c`, `parse.c`, `unparse.c`, `uuid_time.c`, and other libuuid files must match these prototypes.

Risks: changes are ABI/API visible. `uuid_t` as an array type has C parameter decay quirks, so documentation must be precise about output buffers. Any mismatch between this header and implementation can break builds or C++ linkage.

Test signals: compiling `tst_uuid.c` against this header validates basic declarations. ABI tests should ensure `sizeof(uuid_t) == 16` and that public prototypes remain compatible.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.pc.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.pc.in

Purpose: `uuid.pc.in` is the pkg-config metadata template for libuuid.

Important APIs, types, and functions: it defines pkg-config fields `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Description`, `Version`, `Libs`, and `Cflags`. The key consumer outputs are `-L${libdir} -luuid` and `-I${includedir}`.

Control flow: no runtime control flow. Build-time substitution replaces `@prefix@`, `@exec_prefix@`, `@libdir@`, `@includedir@`, and `@E2FSPROGS_VERSION@`.

State and persistence: installed metadata persists for downstream build systems using `pkg-config --libs uuid` or `pkg-config --cflags uuid`.

Dependencies and integration points: depends on the e2fsprogs substitution pipeline. It must align with the actual installation directories used by the library and public headers.

Risks: incorrect substitution or install paths cause downstream compile/link failures. Version mismatches can confuse dependency resolution.

Test signals: run `pkg-config --cflags --libs` against an installed build and compile a small program including `<uuid/uuid.h>` and linking with `-luuid`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuidP.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuidP.h

Purpose: `uuidP.h` is the private libuuid header for internal structure layout and pack/unpack helpers.

Important APIs, types, and functions: it defines `TIME_OFFSET_HIGH`, `TIME_OFFSET_LOW`, and `struct uuid` with fields `time_low`, `time_mid`, `time_hi_and_version`, `clock_seq`, and `node[6]`. It declares `uuid_pack()` and `uuid_unpack()`.

Control flow: preprocessor flow chooses `<inttypes.h>` when available or `<uuid/uuid_types.h>` otherwise, then includes `<sys/types.h>` and the public `<uuid/uuid.h>`.

State and persistence: no runtime state. The struct definition is private but central to internal interpretation of binary UUIDs.

Dependencies and integration points: used by `pack.c`, `unpack.c`, `parse.c`, `unparse.c`, `uuid_time.c`, and likely UUID generation files outside this work item. The time offset constants correspond to the UUID epoch offset from 15-Oct-1582 to Unix epoch.

Risks: changing `struct uuid` field widths or semantics would break every internal conversion. Because the public representation is a byte array, this struct must remain an internal logical view, not a serialized layout.

Test signals: compile all libuuid implementation files and run `tst_uuid.c`. Known UUID timestamp and string round-trip tests validate this header's field model.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuidP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_clear.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_clear.3.in

Purpose: manpage template for `uuid_clear()`, documenting how to reset a UUID variable to the NULL UUID.

Important APIs, types, and functions: documents `void uuid_clear(uuid_t uu)` from `<uuid/uuid.h>`.

Control flow: documentation only; `.TH` uses e2fsprogs version/date substitutions and `.SH` sections describe synopsis, behavior, author, availability, and see-also links.

State and persistence: after installation, persists as API documentation. It describes a function that mutates the caller's UUID buffer to all-zero/null value.

Dependencies and integration points: must match public declaration in `uuid.h.in` and implementation in the libuuid source outside this work item. Cross-references other UUID manpages.

Risks: minimal, but stale docs could mislead about null UUID semantics if implementation changes.

Test signals: documentation generation via substitution and `man` formatting checks; `tst_uuid.c` checks `uuid_clear()` followed by `uuid_is_null()`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_clear.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_compare.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_compare.3.in

Purpose: manpage template for `uuid_compare()`, documenting lexicographic UUID comparison.

Important APIs, types, and functions: documents `int uuid_compare(uuid_t uu1, uuid_t uu2)`, returning less than, equal to, or greater than zero.

Control flow: documentation only. The text is structured as NAME, SYNOPSIS, DESCRIPTION, RETURN VALUE, AUTHOR, AVAILABILITY, and SEE ALSO.

State and persistence: installed documentation only. The described function reads two UUID buffers and returns comparison status.

Dependencies and integration points: must stay aligned with `uuid.h.in` and the actual comparison implementation. `tst_uuid.c` uses `uuid_compare()` after parse and copy operations.

Risks: the manpage says "lexigraphically", a typo for lexicographically. More importantly, if implementation uses `memcmp()` byte ordering, docs should continue to describe bytewise lexical ordering rather than UUID semantic timestamp ordering.

Test signals: compare equal buffers, copied buffers, and ordered known byte arrays. Build substitution should fill version/date placeholders.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_compare.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_copy.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_copy.3.in

Purpose: manpage template for `uuid_copy()`, documenting copying one UUID value to another.

Important APIs, types, and functions: documents `void uuid_copy(uuid_t dst, uuid_t src)` as declared in the public header.

Control flow: documentation only. The page states that `src` is copied to `dst` and that the copied UUID is returned in the destination location.

State and persistence: installed manpage. The described function mutates the destination UUID buffer but has no persistent library state.

Dependencies and integration points: tied to `uuid.h.in` and the copy implementation outside this work item. Used in `tst_uuid.c` before `uuid_compare()`.

Risks: array parameter constness in the manpage is less precise than the header (`const uuid_t src` in `uuid.h.in`). Documentation should avoid implying a returned value because the function returns `void`; the current wording means "stored", not a C return.

Test signals: `tst_uuid.c` copy-and-compare path. Manpage substitution should fill date and version placeholders.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_copy.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_generate.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_generate.3.in

Purpose: manpage template for UUID generation APIs: default, random, and time-based UUID creation.

Important APIs, types, and functions: documents `uuid_generate(uuid_t out)`, `uuid_generate_random(uuid_t out)`, and `uuid_generate_time(uuid_t out)`.

Control flow: documentation only, but it describes the generation selection logic: `uuid_generate()` prefers high-quality randomness from `/dev/urandom`; if unavailable, it falls back to time, local MAC address when available, and pseudo-random data. `uuid_generate_random()` forces all-random format, and `uuid_generate_time()` forces the time/MAC algorithm.

State and persistence: installed documentation. The described implementations may consume system entropy and may depend on machine/network identity and time; those side effects are outside this template.

Dependencies and integration points: should match generation implementation and public constants in `uuid.h.in`. `tst_uuid.c` checks generated random UUIDs are type 4 and generated time UUIDs are type 1, with DCE variant.

Risks: the text has historical wording and typos such as "subsituted" and "elemntary". Privacy warning for time/MAC UUIDs is important and must stay visible. If the implementation changes entropy sources or daemon use, this page needs updates.

Test signals: generation tests should verify version bits, variant bits, parse/unparse round trips, and behavior under entropy-source failure if feasible. Documentation generation should verify placeholders are substituted.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_generate.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_is_null.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_is_null.3.in

Purpose: manpage template for `uuid_is_null()`, documenting comparison against the NULL UUID.

Important APIs, types, and functions: documents `int uuid_is_null(uuid_t uu)`, with return value 1 for null UUID and 0 otherwise.

Control flow: documentation only.

State and persistence: installed API documentation. The function described reads the UUID buffer and does not mutate persistent state.

Dependencies and integration points: paired with `uuid_clear.3.in` and public declaration in `uuid.h.in`. `tst_uuid.c` tests it immediately after `uuid_clear()`.

Risks: no major implementation risks in the template. Header constness is more precise than the manpage if the public prototype uses `const uuid_t`.

Test signals: clear-then-is-null and nonzero UUID checks. Manpage substitution and formatting should be part of doc build validation.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_is_null.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_parse.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_parse.3.in

Purpose: manpage template for `uuid_parse()`, documenting conversion from canonical UUID text to binary representation.

Important APIs, types, and functions: documents `int uuid_parse(char *in, uuid_t uu)`, returning 0 on success and -1 on parse failure. The implementation has `const char *in`, so the documentation is slightly less const-correct.

Control flow: documentation only. It describes the accepted format as 36 bytes plus trailing NUL with hyphenated hex groups.

State and persistence: installed documentation. The described function writes the parsed UUID into caller-provided memory and otherwise has no persistence.

Dependencies and integration points: must match `parse.c`, `uuid.h.in`, and `uuid_unparse.3.in`. It cross-references generation, time, and unparse APIs.

Risks: the manpage's format string `%08x-%04x-%04x-%04x-%012x` is a conceptual description; the implementation actually parses the node as six byte pairs. If accepted forms ever expand beyond canonical hyphenated strings, this page must change.

Test signals: `tst_uuid.c` parse-valid and parse-invalid cases directly validate the documented behavior. Manpage substitution fills e2fsprogs date/version.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_parse.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_time.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_time.3.in

Purpose: manpage template for `uuid_time()`, documenting extraction of a Unix timestamp from time-based UUIDs.

Important APIs, types, and functions: documents `time_t uuid_time(uuid_t uu, struct timeval *ret_tv)`. It says seconds are returned and seconds plus microseconds are stored in `ret_tv`.

Control flow: documentation only. It warns that only certain UUID types encode creation time and that reliable extraction is expected for UUIDs from `uuid_generate_time()`.

State and persistence: installed manpage. The described function reads a UUID and optionally writes a caller-provided `struct timeval`.

Dependencies and integration points: must match `uuid_time.c`, `uuid_generate.3.in`, and the public prototype in `uuid.h.in`. `tst_uuid.c` generates a time UUID and calls `uuid_time()`.

Risks: docs should emphasize that non-time UUIDs can produce meaningless timestamps. Header constness is more precise than the synopsis. Time conversion depends on UUID epoch constants in `uuidP.h`.

Test signals: known version-1 UUID timestamp tests, generated time UUID type checks, and doc substitution/formatting checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_time.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_time.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_time.c

Purpose: `uuid_time.c` inspects UUID internals to extract timestamp, type, and variant metadata. It explicitly crosses the abstraction boundary by interpreting fields inside a UUID.

Important APIs, types, and functions: public functions are `time_t uuid_time(const uuid_t uu, struct timeval *ret_tv)`, `int uuid_type(const uuid_t uu)`, and `int uuid_variant(const uuid_t uu)`. Under `DEBUG`, it also provides a CLI-style `main()` and `variant_string()` for inspecting one UUID string.

Control flow: `uuid_time()` unpacks the UUID, combines the low 32 bits with the high timestamp bits from `time_mid` and low 12 bits of `time_hi_and_version`, subtracts the UUID-to-Unix epoch offset, and converts 100ns ticks into seconds and microseconds. `uuid_type()` unpacks and returns the high 4 version bits from `time_hi_and_version`. `uuid_variant()` unpacks and classifies the high bits of `clock_seq` into NCS, DCE, Microsoft, or other. The debug `main()` parses an input UUID, prints variant/type, warns for non-DCE or non-time UUIDs, and prints decoded time.

State and persistence: no persistent state. It writes to `ret_tv` when non-null and returns scalar metadata. Debug mode prints to stdout/stderr.

Dependencies and integration points: depends on `uuidP.h`, `uuid_unpack()`, public constants from `uuid.h.in`, and system time headers. `tst_uuid.c` validates type, variant, and time extraction for generated UUIDs. Manpage `uuid_time.3.in` documents the timestamp API.

Risks: `uuid_time()` does not validate that the UUID is DCE version 1 before decoding; callers can pass random UUIDs and get meaningless time values. Arithmetic assumes `uint64_t` availability through private integer type setup. Formatting in debug/test paths uses `%ld` for timeval fields, which may be platform-sensitive. The epoch offset is hard-coded rather than using the named `TIME_OFFSET_*` macros, so duplicated constants must remain synchronized.

Test signals: `tst_uuid.c` checks version 1 for `uuid_generate_time()`, version 4 for random UUIDs, and DCE variant for generated UUIDs. Add fixed vector tests for UUID timestamp decoding to guard the 100ns and epoch arithmetic.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_types.h.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_types.h.in

Purpose: `uuid_types.h.in` is a fallback integer type header for libuuid when `<inttypes.h>` is unavailable.

Important APIs, types, and functions: it defines signed and unsigned fixed-width integer typedefs (`int8_t`, `int16_t`, `int32_t`, `int64_t`, `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`) using Autoconf-substituted base C types.

Control flow: preprocessor include guard `_UUID_TYPES_H`; no runtime flow. The file depends on substitutions such as `@u_int8_t@`, `@uint16_t@`, and similar configured type names.

State and persistence: installed/generated header only. It affects compile-time type availability and ABI assumptions.

Dependencies and integration points: `uuidP.h` includes this header when `HAVE_INTTYPES_H` is not defined. Pack/unpack and time code require exact-width integer behavior.

Risks: incorrect configure substitutions break binary layout and arithmetic. Defining standard typedef names can conflict with system headers if inclusion guards or feature detection are wrong.

Test signals: configure/build on systems without `<inttypes.h>` or with simulated fallback. Compile pack/unpack/time code and assert expected type widths.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_types.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_unparse.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_unparse.3.in

Purpose: manpage template for converting binary UUIDs to text with `uuid_unparse()`, `uuid_unparse_upper()`, and `uuid_unparse_lower()`.

Important APIs, types, and functions: documents the three unparse functions and the required output buffer for a 36-byte string plus trailing NUL.

Control flow: documentation only. It states that `uuid_unparse()` default case may be system-dependent, while upper/lower variants provide deterministic case.

State and persistence: installed API documentation. The described functions write caller-provided output buffers.

Dependencies and integration points: must match `unparse.c`, `uuid.h.in`, and `uuid_parse.3.in`. Cross-references the broader UUID API.

Risks: the page has a typo "tailing" for trailing. The buffer-size requirement is critical because implementation uses `sprintf()`. Any build-time default case macro change should still be compatible with this wording.

Test signals: fixed byte-array to lower/upper string tests, parse-unparse round trip, and manpage substitution checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_unparse.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuidd.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuidd.h

Purpose: `uuidd.h` defines constants and private generator hooks used by the `uuidd` daemon protocol.

Important APIs, types, and functions: daemon paths `UUIDD_DIR`, `UUIDD_SOCKET_PATH`, `UUIDD_PIDFILE_PATH`, and `UUIDD_PATH`; operation constants `UUIDD_OP_GETPID`, `UUIDD_OP_GET_MAXOP`, `UUIDD_OP_TIME_UUID`, `UUIDD_OP_RANDOM_UUID`, `UUIDD_OP_BULK_TIME_UUID`, `UUIDD_OP_BULK_RANDOM_UUID`, and `UUIDD_MAX_OP`; private functions `uuid__generate_time(uuid_t out, int *num)` and `uuid__generate_random(uuid_t out, int *num)`.

Control flow: header-only preprocessor definitions, with an include guard. No runtime flow.

State and persistence: defines filesystem locations under `/var/lib/libuuid` for the daemon socket and pidfile. Those paths are persistent integration points for daemon/client coordination.

Dependencies and integration points: includes or relies on `uuid_t` being available from the public UUID headers in compilation units that include it. The operation codes must match uuidd client/server implementations elsewhere in libuuid/e2fsprogs.

Risks: hard-coded paths may not match downstream packaging policies. Operation-code changes are protocol-breaking. The closing include-guard comment says `_UUID_UUID_H`, which appears copied from another header and is misleading.

Test signals: daemon/client integration tests should validate socket path use, op code dispatch, and bulk UUID generation counts. Header compile tests catch missing `uuid_t` include ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuidd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/Makefile.in

Purpose: `util/Makefile.in` builds utility programs used by the e2fsprogs-libs build, primarily the `subst` template substitution tool and generated `gen-tarball` script.

Important APIs, types, and functions: make targets include `all`, `subst`, `copy_sparse`, `gen-tarball`, `tarballs`, `clean`, `mostlyclean`, and `distclean`. Variables are Autoconf-substituted (`@srcdir@`, `@top_srcdir@`, `@INSTALL@`, `@MCONFIG@`) and build-tool variables include `BUILD_CC`, `BUILD_CFLAGS`, and `BUILD_LDFLAGS`.

Control flow: pattern rule compiles `.c` to `.o`; `subst` links `subst.o`; `gen-tarball` runs `config.status` with `CONFIG_FILES=util/gen-tarball` and makes the result executable; `tarballs` invokes the generated script for Debian, all, and subset tarballs. Clean targets remove binaries, objects, generated tarballs, and generated Makefile artifacts.

State and persistence: creates build outputs in the util build directory, especially `subst` and `gen-tarball`. `distclean` removes generated Makefile state.

Dependencies and integration points: relies on the top-level e2fsprogs build system, `MCONFIG`, `config.status`, and `subst.c`. `gen-tarball.in` is transformed into the executable script.

Risks: `copy_sparse` has a build target but is not included in `PROGS`, so it may not be built by default. The `clean` target removes `copy-sparse` while the target is `copy_sparse`, likely a stale hyphen/underscore mismatch. Build/host compiler distinction matters because `subst` runs during the build.

Test signals: run `make -C util all`, verify `subst` and executable `gen-tarball`, and run `make clean/distclean` in a disposable tree to catch stale artifact names.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/copy_sparse.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/copy_sparse.c

Purpose: `copy_sparse.c` copies sparse files efficiently on Linux by using block mapping to skip holes. On non-Linux it exits with an unsupported message.

Important APIs, types, and functions: `get_bmap()` wraps the Linux `FIBMAP` ioctl; `full_read()` retries reads and handles interruptions; `copy_sparse_file()` performs the copy; `usage()` and `main()` parse `-v source destination`. It uses large-file APIs (`stat64`, `open` with `O_LARGEFILE`, `lseek64`), `FIGETBSZ`, and root-only `FIBMAP`.

Control flow: for regular source files, it stats and opens the source, obtains filesystem block size via `FIGETBSZ`, and computes block count. For stdin (`-`), it uses fd 0 with a 1024-byte block size. The destination is opened/truncated. For each source block, file input uses `FIBMAP` to skip unmapped blocks; stdin scans zero-filled blocks to preserve holes. Non-hole data is read and written, seeking the destination over skipped ranges. At the end it ensures destination size reaches the source size by seeking and writing a final zero if needed.

State and persistence: reads source data and creates/replaces the destination file with mode `0777` subject to umask. It may create sparse holes via seeks. It does not preserve ownership, mode, timestamps, xattrs, or ACLs.

Dependencies and integration points: Linux-only path depends on kernel ioctls from `<linux/fd.h>` and root permissions for `FIBMAP`. The util Makefile has a target for it but does not build it by default.

Risks: `fileinfo` is uninitialized in the stdin path, but later `offset = fileinfo.st_size` is executed unconditionally, which is a correctness bug if copying from stdin. Many read/write/lseek calls have incomplete error handling; short writes are detected only by comparing one `write()` result. `FIBMAP` requires privileges and may not work on modern filesystems or with delayed allocation. Destination permissions are overly broad before umask. It does not use newer `SEEK_HOLE`/`SEEK_DATA`.

Test signals: test sparse file logical size and block usage before/after copy, compare file contents, run as non-root to verify permission error handling, and test stdin path because it has distinct control flow and likely size-finalization issues.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/copy_sparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/gcc-wall-cleanup -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/gcc-wall-cleanup

Purpose: `gcc-wall-cleanup` is a sed filter that removes expected or low-value compiler warning noise from GCC wall-warning output.

Important APIs, types, and functions: it is a `#!/bin/sed -f` script containing deletion rules for command echo lines and warning patterns involving `long long`, traditional C string concatenation, unsigned constants, include/function context lines, zero-length format strings, and missing initializer details.

Control flow: sed processes input line-by-line and deletes matching lines. Non-matching lines pass through unchanged.

State and persistence: no persistent state; pure stream filter.

Dependencies and integration points: used by build/test tooling that wants cleaner compiler-warning reports. It depends on sed regex dialect and exact warning text from older GCC modes.

Risks: filtering can hide useful warnings if patterns are too broad. Warning text changes across compiler versions may reduce effectiveness. The script is tuned to legacy GCC diagnostics and traditional C compatibility.

Test signals: feed representative compiler logs and verify expected noise is removed while unexpected warnings remain visible.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/gcc-wall-cleanup -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/gen-tarball.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/gen-tarball.in

Purpose: `gen-tarball.in` is a build-substituted shell script for generating e2fsprogs source tarballs, including Debian/Ubuntu, full, and library subset variants.

Important APIs, types, and functions: command argument selects `debian|ubuntu`, `subset`, or `all` behavior. It uses substituted variables `@srcdir@`, `@top_srcdir@`, `@E2FSPROGS_VERSION@`, and `@E2FSPROGS_PKGVER@`. External tools include `sed`, `basename`, `find`, `tar`, `gzip`, `ln`, `mv`, and `rm`.

Control flow: computes version and source root names, chooses exclude-list mode, temporarily moves `e2fsprogs.spec`, builds an exclude file under `/tmp/exclude`, appends list-specific excludes, creates a symlink named as the desired tar root, archives with dereference/hard link behavior via `tar -c -h`, compresses with gzip, lists gzip stats, removes symlink, restores the spec file, and optionally renames the tarball for Debian packaging.

State and persistence: creates tarballs in the working directory, writes `/tmp/exclude`, creates/removes a symlink in the parent source directory, and temporarily moves `e2fsprogs.spec`.

Dependencies and integration points: generated by `util/Makefile.in` through `config.status`. It depends on exclude files in the source tree and the e2fsprogs release layout.

Risks: fixed `/tmp/exclude` is collision-prone across concurrent runs and vulnerable to clobbering. Temporary movement of `e2fsprogs.spec` can leave the tree inconsistent if interrupted. Unquoted variables can break on paths with spaces. Tarball reproducibility is limited compared with newer scripts.

Test signals: run in a disposable tree for `all`, `subset`, and `debian`; inspect tar root naming, excluded files, restored spec file, and generated gzip metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/gen-tarball.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/libecho.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/libecho.c

Purpose: `libecho.c` is a DOS/Windows-oriented helper that echoes command-line file arguments after wildcard expansion, optionally prefixed.

Important APIs, types, and functions: `main()` parses `-p prefix` and calls `echo_files()`. `echo_files()` uses `_findfirst()`, `_findnext()`, `_findclose()`, `_finddata_t`, and `stricmp()` from DOS/Windows C library headers.

Control flow: `main()` defaults prefix to empty, requires at least one argument, recognizes `-p`, and otherwise expands each file pattern. `echo_files()` normalizes forward slashes to backslashes in-place, extracts any directory prefix, then uses `_findfirst()` to expand the pattern. If no match is found, it prints the original argument. If matches exist, it prints the prefix plus directory plus each matched name.

State and persistence: no file mutations; output is printed to stdout. It mutates the input argument string in memory while normalizing slashes.

Dependencies and integration points: depends on `<io.h>` and Windows/DOS filesystem APIs. Likely used by older build machinery to handle wildcard expansion in environments where the shell does not expand globs.

Risks: `filepath[256]` and `strcpy()` can overflow for long paths. Modifying `argv` strings is not portable. Only `-p` exact case-insensitive option is handled and missing prefix after `-p` can read past argv. Not suitable for POSIX builds.

Test signals: Windows build/run tests with unmatched patterns, matched wildcard patterns, directory prefixes, forward slashes, and `-p` prefix.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/libecho.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/subst.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/subst.c

Purpose: `subst.c` is a small build-time template substitution program used to expand `@NAME@` and `${NAME}`-style placeholders into configured values.

Important APIs, types, and functions: `struct subst_entry` stores linked-list substitutions. `add_subst()`, `fetch_subst_entry()`, `get_subst_symbol()`, `replace_string()`, `substitute_line()`, `parse_config_file()`, `compare_file()`, and `main()` implement the tool. CLI options are `-f config-file`, `-t` to adjust timestamp on unchanged output, and `-v` for verbose logging.

Control flow: config files are parsed into a linked list of name/value substitutions, ignoring comments, blank lines, and future-extension lines beginning with `@`. Input is read from a file or stdin. Each line first expands `@FOO@`, handling `@@` as a literal `@`, then expands `${FOO}` by looking up a key with `$` prefix. Output goes to stdout or to `outfn.new`. When writing a named output, it compares the new file with the existing file; unchanged output keeps the old file and optionally updates mtime, changed output renames `.new` into place. The final output file is chmodded read-only for user/group/other write bits.

State and persistence: maintains an in-memory substitution table for the process. It writes generated files, may update timestamps, removes temporary `.new` files on unchanged output, and changes output file mode to read-only.

Dependencies and integration points: used by e2fsprogs build templates such as manpages, headers, pkg-config files, and generated scripts. It consumes `subst.conf.in` after configuration and uses standard C/POSIX file APIs.

Risks: fixed 2048-byte line buffers can truncate long lines. `replace_string()` can grow a line in-place without knowing the full allocated capacity, so large replacement values can overflow the stack buffer. The substitution table never frees entries, acceptable for short build-tool process lifetime. `parse_config_file()` comment stripping treats `#` anywhere as comment, so values cannot contain literal `#`. Missing `@FOO@` emits an error but does not fail the process.

Test signals: unit-style runs for `@NAME@`, `@@`, `${prefix}` with `$`-prefixed config keys, unchanged output preservation, timestamp update mode, missing substitutions, long replacements, and generated file permissions.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/subst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/subst.conf.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/subst.conf.in

Purpose: `subst.conf.in` is the configuration template consumed by `subst` to map placeholder names to configured build values.

Important APIs, types, and functions: contains substitution keys for tools (`AWK`, `SED`), directories (`ET_DIR`, `SS_DIR`, `datarootdir`, `datadir`, `root_sysconfdir`, `$root_prefix`, `$prefix`), e2fsprogs version/date (`E2FSPROGS_MONTH`, `E2FSPROGS_YEAR`, `E2FSPROGS_VERSION`), C type sizes, and `JDEV`.

Control flow: no executable flow. During configuration, `@...@` tokens are expanded; later `subst.c` reads the resulting file and uses whitespace-separated key/value pairs.

State and persistence: generated config data persists in the build tree and drives later template expansion.

Dependencies and integration points: depends on Autoconf results and is consumed by `util/subst`. `$prefix` and `$root_prefix` keys intentionally support `${prefix}`-style substitution because `subst.c` stores names with `$` prefix for brace expansion.

Risks: blank `JDEV` intentionally disables documentation text; accidental whitespace or comments in values can be truncated by `subst.c`. Values containing `#` are not safe because the parser strips comments.

Test signals: configure substitution followed by generating representative manpages/headers. Verify both `@E2FSPROGS_VERSION@` and `${prefix}` style placeholders resolve.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/subst.conf.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/version.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/version.h

Purpose: `version.h` defines the e2fsprogs version and release date strings used by programs in this vendored e2fsprogs-libs snapshot.

Important APIs, types, and functions: macros `E2FSPROGS_VERSION "1.41.14"` and `E2FSPROGS_DATE "22-Dec-2010"`.

Control flow: header-only macro definitions; no runtime control flow.

State and persistence: compile-time constants become embedded in binaries that include this header.

Dependencies and integration points: included by e2fsprogs utilities outside this work item for version reporting. It aligns with template substitutions used by manpages and package metadata.

Risks: stale version strings can mislead diagnostics and packaged artifacts. Because this is a vendored snapshot inside xfstests-bld, version drift may be intentional.

Test signals: compile a version-reporting utility and check output; compare with generated package/manpage metadata when building the snapshot.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/wordwrap.pl -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/wordwrap.pl

Purpose: `wordwrap.pl` wraps dependency or makefile-style lines to about 78 columns while preserving comments and adjusting a few source-path references.

Important APIs, types, and functions: Perl reads stdin line-by-line. It skips comment lines and blank lines, splits other lines on whitespace, rewrites selected `$(srcdir)/.../version.h` and `com_err.h` paths to `$(top_srcdir)/...`, and emits words with backslash-newline continuations when the line length exceeds 78.

Control flow: for each non-comment nonblank line, initialize `linelen`, iterate words, optionally print a space, compute next word length, emit `\\\n ` when wrapping, then print the word and final newline.

State and persistence: pure stream transformer; no persistent state or file I/O beyond stdin/stdout.

Dependencies and integration points: used in build dependency generation cleanup where wrapped Makefile dependency lines are desired. It is tied to e2fsprogs source layout path rewrites.

Risks: `split` without assignment uses `@_`, which works in this script but is terse. Blank lines are dropped rather than preserved. It treats all whitespace as separators, so quoted values are not preserved.

Test signals: feed dependency lines longer than 78 chars, comment lines, blank lines, and the specific version/com_err path patterns.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/wordwrap.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/gen-tarball -->
# sources/test-tools/xfstests-bld/fstests-bld/gen-tarball

Purpose: top-level `gen-tarball` builds an xfstests appliance/runtime tarball from built binaries, xfstests, blktests, optional LTP, and version metadata.

Important APIs, types, and functions: shell options `--fast` and `--arch`; config inputs `config.custom` or `config`; environment knobs `ACCEL_BIN`, `TOOLCHAIN_DIR`, `CROSS_COMPILE`, `SOURCE_DATE_EPOCH`; external tools `git`, `make`, `strip`, `find`, `tar`, `gzip`/`pigz`, `cp`, `ln`, and `sort`.

Control flow: loads config, optionally prepends accelerated binaries/toolchain to `PATH`, selects `strip`, parses options, chooses `pigz` if available, sets `SOURCE_DATE_EPOCH` from last git commit if unset, optionally installs LTP into `ltp`, creates `xfstests` either by copying dev tree in fast mode or running `make install`, writes version metadata, copies built binaries/libs/manual pages, handles optional `ima-evm-utils`, creates symlinks for selected LTP/source tools, strips executables, optionally writes build architecture, and creates a reproducible-ish tarball with sorted file list, numeric root ownership, fixed mtime, and write-bit normalization. With `--arch`, it hard-links/copies the tarball to `xfstests-$ARCH.tar.gz`.

State and persistence: deletes and recreates `xfstests`, optionally deletes/recreates `ltp`, writes `xfstests-bld.ver`, `xfstests/git-versions`, `xfstests.tar.gz`, and optional arch-named tarball.

Dependencies and integration points: assumes surrounding fstests-bld directory layout with `xfstests-dev`, `bld`, optional `ltp-dev`, `blktests`, and possibly `../test-appliance/debs`. It consumes outputs from build-all style processes.

Risks: destructive `rm -rf xfstests` and `rm -rf ltp` are expected but dangerous outside the intended directory. `find ... | xargs $STRIP` can fail on no files or unusual names, though errors are ignored in places. Fast mode copies a development tree and may include files that install mode excludes except `.git`/autom4te.cache cleanup. Optional directories are assumed in several copy/link commands.

Test signals: run with `--fast` and full mode in a disposable built tree; inspect tarball contents, ownership, mtimes, `git-versions`, symlinks, optional arch output, and reproducibility across repeated runs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/gen-tarball -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/get-all -->
# sources/test-tools/xfstests-bld/fstests-bld/get-all

Purpose: `get-all` clones and pins the external repositories needed by fstests-bld according to configured repository URLs and optional commit variables.

Important APIs, types, and functions: functions `have_commit()`, `checkout_commit()`, and `setup_repo()`. CLI supports `-n`/`--no-action`. Required repos include fio, libaio, quota, xfsprogs-dev, xfstests-dev, fsverity, and blktests. Optional repos include ima-evm-utils, keyutils, stress-ng, util-linux, syzkaller, nvme-cli, and ltp-dev.

Control flow: loads `config.custom` if present else `config`, parses no-action mode, then calls `setup_repo()` for each repo. `setup_repo()` removes a plain directory where a git repo is expected, clones missing repos, handles absent optional URLs, and checks out configured commits. `checkout_commit()` refuses to proceed with uncommitted changes, updates remote origin URL if needed, fetches missing commits, validates commit existence, and checks out the target commit unless in no-action mode.

State and persistence: creates, removes, fetches, and checks out git working trees under the fstests-bld directory. It can change remote origin URLs. In normal mode it mutates repository state; in no-action mode it prints intended actions and uses non-destructive checks where possible.

Dependencies and integration points: depends on config variables named `<REPO>_GIT` and `<REPO>_COMMIT`. It is a prerequisite for build scripts that require pinned external source trees.

Risks: `rm -rf "$repo_name"` for plain directories is destructive by design. `git status -s >& /dev/null` suppresses output but still requires a valid repo. Commit checkout refuses dirty trees, which protects user work but can block automation. Optional repo removal from config while directory exists is treated as an error.

Test signals: run `./get-all --no-action` with representative configs; test missing required URL, optional absent URL, dirty repo refusal, changed remote URL, missing commit fetch, and plain-directory replacement in a scratch tree.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/get-all -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/get-versions -->
# sources/test-tools/xfstests-bld/fstests-bld/get-versions

Purpose: `get-versions` prints a sorted summary of git descriptions and commit dates for fstests-bld and its component repositories.

Important APIs, types, and functions: shell script using `git describe --always --dirty` or `--tags` for some repos, `git log -1 --pretty=%cD`, temporary directory `tmp-$$`, and optional copying of `.ver` files from e2fsprogs and test appliance debs.

Control flow: creates a temp directory, writes `xfstests-bld.ver`, copies `e2fsprogs.ver` if present, enters each known repository and writes a component `.ver` file, conditionally handling optional dirs, copies external deb version files, concatenates sorted `.ver` files, removes the temp directory, and exits 0.

State and persistence: creates and removes `tmp-$$`. It reads git metadata from many sibling repositories and emits summary to stdout.

Dependencies and integration points: assumes required directories like `fio`, `quota`, `ima-evm-utils`, `xfsprogs-dev`, and `xfstests-dev` exist. `gen-tarball` creates similar version metadata for inclusion in tarballs.

Risks: no `set -e`, so failures may be partially ignored. It unconditionally `cd`s into `ima-evm-utils`, which `get-all` treats as optional; absence will cause noisy failures and follow-on path errors. `TMPDIR=tmp-$$` can collide only rarely but is not cleaned on interruption.

Test signals: run in a populated checkout and compare expected component rows. Test missing optional and missing required directories, dirty trees, and cleanup of temporary directory.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/get-versions -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/libinih/Makefile -->
# sources/test-tools/xfstests-bld/fstests-bld/libinih/Makefile

Purpose: builds and installs a static `libinih.a` library from the vendored inih parser.

Important APIs, types, and functions: targets `libinih.a`, `install`, `clean`, and dependency `ini.o: ini.c ini.h`. Variables `OBJS`, `LIBDIR=$(DESTDIR)/lib`, and `INCDIR=$(DESTDIR)/include`.

Control flow: `libinih.a` archives `ini.o` with `ar rc` and indexes with `ranlib`; `install` creates lib/include dirs and copies `ini.h` and `libinih.a`; `clean` removes object and archive.

State and persistence: creates `ini.o`, `libinih.a`, and installed files under `DESTDIR`.

Dependencies and integration points: depends on the system `make`, compiler implicit rules, `ar`, and `ranlib`. Used by fstests-bld components needing INI parsing.

Risks: no explicit `CC`, `CFLAGS`, or install mode variables; relies on make defaults. `install` copies without rebuilding prerequisite unless invoked after archive target. No `mkdir -p` for object dir needed because it builds in place.

Test signals: run `make`, `make install DESTDIR=/tmp/...`, compile a small program against installed header and archive, and run `make clean`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/libinih/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/libinih/ini.c -->
# sources/test-tools/xfstests-bld/fstests-bld/libinih/ini.c

Purpose: `ini.c` is the vendored inih parser implementation for simple INI-style configuration files.

Important APIs, types, and functions: public functions are `ini_parse_stream()`, `ini_parse_file()`, `ini_parse()`, and `ini_parse_string()`. Internal helpers include `rstrip()`, `lskip()`, `find_chars_or_comment()`, `strncpy0()`, and `ini_reader_string()`. It uses compile-time feature macros from `ini.h` such as `INI_USE_STACK`, `INI_ALLOW_REALLOC`, `INI_ALLOW_INLINE_COMMENTS`, `INI_ALLOW_MULTILINE`, `INI_ALLOW_BOM`, `INI_HANDLER_LINENO`, and allocator options.

Control flow: `ini_parse_stream()` obtains lines from a caller-provided reader, optionally grows the line buffer, strips BOM on first line, trims whitespace, skips comments, handles continuation lines when enabled, parses `[section]` headers, parses `name=value` or `name:value`, strips inline comments and whitespace, and calls the handler callback. It records the first parse or handler error line while optionally continuing. Wrappers adapt `FILE *`, filenames, and strings to the stream parser.

State and persistence: parser state is local: current section, previous name for multiline continuations, line buffer, line number, and first error. It performs no persistent writes. Heap allocation is used only when configured not to use stack buffers.

Dependencies and integration points: paired with `ini.h` and built into `libinih.a`. Consumers supply callbacks that receive transient pointers valid only during the handler call.

Risks: default `MAX_SECTION` and `MAX_NAME` are 50, so long section/name values are truncated. Default `INI_MAX_LINE` is 200, so long lines can be truncated unless heap realloc is enabled. Callback failure semantics depend on macros. Inline comment detection only treats comment prefixes after whitespace. Since handler receives pointers into the mutable line buffer, consumers must copy data if needed.

Test signals: parse files with BOM, comments, inline comments, multiline values, section headers, colon/equal separators, no-value lines under both macro modes, long names/sections/lines, string input, missing file, and handler failure.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/libinih/ini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/libinih/ini.h -->
# sources/test-tools/xfstests-bld/fstests-bld/libinih/ini.h

Purpose: `ini.h` is the public header for the vendored inih parser, defining callback types, parser entry points, and compile-time configuration macros.

Important APIs, types, and functions: typedefs `ini_handler` and `ini_reader`; functions `ini_parse()`, `ini_parse_file()`, `ini_parse_stream()`, and `ini_parse_string()`. Configuration macros include `INI_HANDLER_LINENO`, `INI_ALLOW_MULTILINE`, `INI_ALLOW_BOM`, `INI_START_COMMENT_PREFIXES`, `INI_ALLOW_INLINE_COMMENTS`, `INI_INLINE_COMMENT_PREFIXES`, `INI_USE_STACK`, `INI_MAX_LINE`, `INI_ALLOW_REALLOC`, `INI_INITIAL_ALLOC`, `INI_STOP_ON_FIRST_ERROR`, `INI_CALL_HANDLER_ON_NEW_SECTION`, `INI_ALLOW_NO_VALUE`, and `INI_CUSTOM_ALLOCATOR`.

Control flow: header-only preprocessor configuration and C++ `extern "C"` wrapping. Macro values selected at compile time alter `ini.c` behavior and callback signatures.

State and persistence: no runtime state in the header. It defines contracts for parser callbacks, including that passed strings are valid only during callback execution.

Dependencies and integration points: included by `ini.c` and by consumers linking against `libinih.a`. Requires `<stdio.h>` for `FILE`.

Risks: changing macros between compiling `ini.c` and compiling consumers can break ABI, especially `INI_HANDLER_LINENO`. Small default line/section/name capacities may surprise consumers. Custom allocator mode requires external functions with exact names/signatures.

Test signals: compile with default macros and with key macro combinations, especially `INI_HANDLER_LINENO`, heap allocation/realloc, no-value support, and C++ inclusion.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/libinih/ini.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/misc/Makefile.in

Purpose: `misc/Makefile.in` builds and installs local benchmark/test utilities for fstests-bld.

Important APIs, types, and functions: variables `CC`, `CFLAGS`, `LDFLAGS`, `PROGS=fname_benchmark postmark resize syncfs`, and `SCRIPTS=encrypt-fname-benchmark`. Targets include `all`, individual binaries, `install`, `zerofree`, `clean`, and regenerated `Makefile`.

Control flow: `all` builds `PROGS`. Each C target invokes `$(CC) $(LDFLAGS) -o <prog> -O2 $<`. `install` copies programs and scripts to `$(DESTDIR)/bin` and chmods executable. `zerofree` links against `-lext2fs`. `Makefile` regeneration calls top-level `config.status`.

State and persistence: creates local binaries and installs them under `DESTDIR`. `clean` removes configured program outputs and `zerofree`.

Dependencies and integration points: generated from `configure`/`configure.ac`. Depends on source files not all in this work item (`resize.c`, `syncfs.c`, zerofree source). Integrates benchmark utilities into fstests appliance images.

Risks: `CFLAGS` is defined but not used in compile commands; only `-O2` is passed. `all` does not build `zerofree`. Install assumes binaries/scripts exist and does not preserve modes except chmod +x.

Test signals: configure then `make -C misc all install DESTDIR=...`, verify binaries execute/help, and `make clean` removes outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/configure -->
# sources/test-tools/xfstests-bld/fstests-bld/misc/configure

Purpose: `misc/configure` is a generated GNU Autoconf 2.69 script that configures the misc benchmark/test utility subdirectory and emits `Makefile`.

Important APIs, types, and functions: shell functions and generated machinery include option parsing, shell portability setup, `as_fn_*` helpers, source directory discovery using `fname_benchmark.c`, auxiliary script lookup under `../e2fsprogs-libs/config`, canonical build/host detection via `config.guess`/`config.sub`, C compiler discovery, compile/link tests, and `config.status` generation for `Makefile`.

Control flow: initializes a portable shell environment, parses standard configure options and environment variables, validates source directory, writes `config.log`, finds auxiliary install/config scripts, canonicalizes build and host tuples, discovers an acceptable C compiler (`gcc`, `cc`, `cl.exe`, including cross prefixes), verifies compile/link behavior and object/executable suffixes, prepares substitution variables, and writes/runs `config.status` unless `--no-create` is used. `config.status` substitutes `Makefile.in` into `Makefile`.

State and persistence: creates or updates `config.log`, `config.status`, temporary `conftest*` files during checks, and generated `Makefile`. It reads optional cache/site files and may use `config.cache` when requested.

Dependencies and integration points: generated from `misc/configure.ac`; requires the e2fsprogs-libs config auxiliary directory. `misc/Makefile.in` consumes the substituted variables. It is the entry point for portable builds of `fname_benchmark`, `postmark`, and other misc utilities.

Risks: generated script is large and mostly boilerplate; manual edits should be avoided in favor of editing `configure.ac` and regenerating. It assumes Autoconf-era shell portability and may carry legacy behavior. Missing auxiliary scripts or compiler failures abort configuration. Environment changes with cache enabled can invalidate builds.

Test signals: run `./configure` in `misc`, inspect generated `Makefile`, run `make`, test `--help`, `--no-create`, out-of-tree builds if supported, and cross-compile host/build options.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/configure.ac -->
# sources/test-tools/xfstests-bld/fstests-bld/misc/configure.ac

Purpose: source Autoconf input for generating `misc/configure`.

Important APIs, types, and functions: uses `AC_PREREQ(2.59)`, `AC_INIT(fname_benchmark.c)`, `AC_CONFIG_AUX_DIR(../e2fsprogs-libs/config)`, `AC_CANONICAL_BUILD`, `AC_CANONICAL_HOST`, `AC_PROG_CC`, and `AC_OUTPUT(Makefile)`.

Control flow: when processed by Autoconf, it creates a configure script that validates source presence, locates auxiliary scripts, canonicalizes build/host, finds a C compiler, and generates `Makefile`.

State and persistence: no runtime state itself; regenerating from it updates the generated `configure` script.

Dependencies and integration points: tied to `misc/Makefile.in`, `misc/configure`, and the e2fsprogs-libs config auxiliary directory.

Risks: minimal and intentionally simple. Any new misc utility requiring library/header checks must add tests here and regenerate `configure`.

Test signals: run `autoconf` and compare/regenerate `configure`, then run generated configure and make.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/encrypt-fname-benchmark -->
# sources/test-tools/xfstests-bld/fstests-bld/misc/encrypt-fname-benchmark

Purpose: shell wrapper that runs `fname_benchmark` inside an ext4 encrypted directory on `/dev/ram0`.

Important APIs, types, and functions: external commands `mke2fs`, `mount`, `mkdir`, `e4crypt add_key`, `fname_benchmark`, and `umount`.

Control flow: formats `/dev/ram0` as ext4 with encryption enabled, mounts it at `/mnt`, creates `/mnt/a`, pipes `foobar` to `e4crypt add_key /mnt/a`, enters the encrypted directory, runs `fname_benchmark`, returns to `/`, and unmounts `/mnt`.

State and persistence: destructively reformats `/dev/ram0`, mounts/unmounts `/mnt`, creates files/directories under the mounted filesystem, and runs the benchmark workload.

Dependencies and integration points: assumes root privileges, a usable RAM block device at `/dev/ram0`, ext4 encryption support, `e4crypt`, and installed `fname_benchmark`. Intended as a specialized benchmark script installed by `misc/Makefile.in`.

Risks: destructive to `/dev/ram0` and unsafe if `/mnt` is in use. No `set -e`, cleanup trap, argument configurability, or error handling; failures can leave mounts behind. Hard-coded passphrase is insecure but likely acceptable for a local benchmark scratch filesystem.

Test signals: run only in a controlled VM/test environment. Verify mount cleanup on success/failure, encrypted directory setup, and benchmark output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/encrypt-fname-benchmark -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/fname_benchmark.c -->
# sources/test-tools/xfstests-bld/fstests-bld/misc/fname_benchmark.c

Purpose: `fname_benchmark.c` is a microbenchmark measuring CPU time spent creating, reading/looking up, and unlinking many files, optionally with file payloads and cache dropping.

Important APIs, types, and functions: operations `file_create()`, `file_read()`, `file_unlink()`; timing helpers `timeval_add()`, `timeval_sub()`, `upd_stat()`, `print_stat()`; `drop_cache()`; `main()` parsing `-b`, `-n`, `-r`, and `-d`. Global configuration includes `buf`, `bufsize`, and `time_stat` accumulators.

Control flow: `main()` parses buffer size, number of files, repeat count, and drop-cache flag. It optionally allocates a buffer, then for each repeat measures create loop for files named `f%04d`, optionally drops caches, measures read loop, optionally drops caches again, and measures unlink loop. At the end it prints configuration and accumulated user/system CPU times for create, lookup, unlink, and total process usage.

State and persistence: creates and deletes benchmark files in the current directory. If `-b` is used, writes/reads `bufsize` bytes from an allocated buffer. `drop_cache()` calls `sync()` and writes `"3\n"` to `/proc/sys/vm/drop_caches`.

Dependencies and integration points: built by `misc/Makefile.in` and called by `encrypt-fname-benchmark`. Depends on POSIX file APIs, `getrusage()`, and Linux `/proc/sys/vm/drop_caches` when cache dropping is enabled.

Risks: `drop_cache()` opens `/proc/sys/vm/drop_caches` with `O_RDONLY` but then writes to it; this appears wrong and should be `O_WRONLY`, so default `do_drop=1` may fail. Filenames use `f%04d`, but larger `num_files` still fit in the 256-byte buffer. Existing files with same names are truncated/deleted. Buffer contents are uninitialized, which is fine for throughput but can trip tools expecting deterministic data.

Test signals: run with `-d 0` in a scratch directory as non-root, then with cache dropping as root after fixing/validating open mode. Validate all created files are removed, option validation rejects invalid values, and timing output is sane.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/fname_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/post-reorg-cleanup -->
# sources/test-tools/xfstests-bld/fstests-bld/misc/post-reorg-cleanup

Purpose: `post-reorg-cleanup` is a one-time migration helper for cleaning and moving directories after a repository reorganization that introduced/moved `fstests-bld`.

Important APIs, types, and functions: shell variables `CLEAN_DIRS`, `TO_MOVE`, and `NO_ACTION`; CLI supports `--no-action`. It uses `cp`, `mv`, `git clean`, `rm`, and directory checks.

Control flow: validates that `fstests-bld` exists. If `config.custom` exists at top level and not under `fstests-bld`, it explains the split and copies it. It moves configured source directories into `fstests-bld`, moves appliance cache/deb/config directories to `test-appliance`, moves logs/disks to `run-fstests`, renames `kvm-xfstests`, and then either previews or performs `git clean` on old directories and selected nested repos. Finally it removes old version/tarball/script/build outputs.

State and persistence: performs broad filesystem mutation: moves directories, copies config, runs destructive `git clean -fdx`, removes generated files, and deletes build/runtime directories. In `--no-action`, most operations are echoed and `git clean -n` is used.

Dependencies and integration points: intended for a specific repository state immediately after a reorganization commit. It assumes top-level `fstests-bld`, `kvm-xfstests`, `test-appliance`, and `run-fstests` naming.

Risks: destructive and context-sensitive. There is a typo in no-action output using `$CLEAR_DIRS` instead of `$CLEAN_DIRS`, which can make preview misleading. The message says `fststs-bld/` once. It uses many unquoted paths but names are controlled. Running in the wrong repository can remove valuable files after only a simple directory check.

Test signals: use `--no-action` in a fixture repo matching pre/post reorg layouts; inspect printed moves and clean previews. Full execution should only be tested on disposable clones with known expected file moves.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/post-reorg-cleanup -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/postmark.c -->
# sources/test-tools/xfstests-bld/fstests-bld/misc/postmark.c

Purpose: `postmark.c` is the PostMark filesystem benchmark, an interactive/config-file-driven workload that creates an initial file set, performs randomized read/append and create/delete transactions, reports throughput, and cleans up. This copy is version `v1.60 : 2017-02-27` with a bundled MT19937 pseudo-random generator.

Important APIs, types, and functions: command dispatch uses `cmd command_list[]` mapping commands such as `set size`, `set number`, `set seed`, `set transactions`, `set location`, `set subdirectories`, `set read`, `set write`, `set buffering`, `set bias read`, `set bias create`, `set report`, `run`, `load`, `show`, `help`, and `quit`. Core workload functions include `initialize_file_source()`, `create_file_name()`, `create_file()`, `delete_file()`, `read_file()`, `append_file()`, `find_free_file()`, `find_used_file()`, `run_transactions()`, `build_location_index()`, `create_subdirectories()`, `delete_subdirectories()`, `cli_run()`, and report functions. PRNG functions are `sgenrand()`, `lsgenrand()`, and `genrand()`.

Control flow: `main()` prints the version, reads `.pmrc` or a single config file if provided, then enters an interactive prompt. CLI parsing supports shell escapes with `!`, aliases `?` to help and `exit` to quit, and dispatches by prefix matching the command table. `cli_run()` resets counters, seeds PRNG, allocates buffers and a file table, builds a weighted location index, creates subdirectories, creates the initial simultaneous file set, runs randomized transactions, deletes remaining files/subdirectories, emits verbose or terse reports, and frees run resources. Each transaction may perform read vs append unless disabled, then create vs delete unless disabled, based on configured biases.

State and persistence: heavy global process state stores configuration, counters, file table, file-system location list, buffers, and PRNG state. Files are created, appended, read, and deleted in the current or configured directories. Optional subdirectories `sN` are created and removed. Reports can append to a specified output file. Shell escapes can run arbitrary commands from the prompt/config.

Dependencies and integration points: built by `misc/Makefile.in` as `postmark`. It depends on C/POSIX file APIs, `gettimeofday()`, `getcwd()`, `system()`, and platform-specific mkdir/separator handling for Windows vs Unix. It is installed as a benchmark utility for filesystem testing.

Risks: legacy K&R-style function definitions and broad global state make maintenance error-prone. Several fixed-size buffers (`MAX_LINE`, `MAX_FILENAME`) are filled with `strcpy()`, `strcat()`, and `sprintf()` without robust bounds checks, so long locations or many subdirectories can overflow. `run_transactions()` computes `percent=transactions/10` and then uses `i % percent`; transactions below 10 cause division by zero. `find_used_file()` spins until it finds a live file and depends on callers preventing empty file sets. I/O functions do not check partial reads/writes/fwrite failures. Config files can invoke shell escapes. `cli_show()` prints configured locations with `printf()` instead of the selected `fp`, so redirected show output is incomplete.

Test signals: run scripted config files with small safe workloads, including verbose and terse reports, buffered/unbuffered modes, weighted locations, subdirectories, disabled biases, and output redirection. Add regression tests for transactions less than 10, long path handling, incomplete transaction depletion, and cleanup after interrupted/error runs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/postmark.c -->
