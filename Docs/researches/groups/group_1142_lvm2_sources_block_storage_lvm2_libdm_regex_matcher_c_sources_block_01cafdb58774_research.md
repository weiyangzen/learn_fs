# Group Research: group_1142_lvm2_sources_block_storage_lvm2_libdm_regex_matcher_c_sources_block_01cafdb58774

Scope: `Docs/research_subset_a.md`; source tree `sources/block-storage/lvm2` is included in subset A.

Read coverage: complete read of all listed files, 6,798 total source lines.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/matcher.c -->
# File Research: sources/block-storage/lvm2/libdm/regex/matcher.c

Purpose: implements libdevmapper's regex matcher by compiling one or more parsed regex patterns into a lazy DFA and returning the index of the best matching pattern.

Read coverage: complete file read, 576 lines.

Key responsibilities:
- Defines `struct dm_regex`, DFA state storage, charset/node tables, scratch bitsets, character maps, and a ternary-tree lookup cache for DFA-state identity.
- Combines all input patterns into one alternation, wrapping each as `(.*(<pattern>)<TARGET_TRANS>)` so matches can report which original pattern accepted.
- Counts and enumerates regex tree nodes and charset leaves, then allocates `firstpos`, `lastpos`, and `followpos` bitsets for direct DFA construction.
- Computes nullable/firstpos/lastpos/followpos functions for CAT, OR, STAR, PLUS, QUEST, and CHARSET nodes.
- Builds DFA states on demand during matching, caching state transitions in `lookup[256]` and interning bitset keys in `ttree`.
- Handles artificial start/end matching via `HAT_CHAR` and `DOLLAR_CHAR`, and forces `TARGET_TRANS` transitions to discover accepting pattern numbers.
- Provides `dm_regex_fingerprint()` test/debug support by forcing all lazy states and hashing reachable DFA transitions.

Important entry points:
- `dm_regex_create(struct dm_pool *mem, const char * const *patterns, unsigned num_patterns)`
- `dm_regex_match(struct dm_regex *regex, const char *s)`
- `dm_regex_fingerprint(struct dm_regex *regex)`

Dependencies:
- Uses `parse_rx.h` for regex tree structure and sentinel characters.
- Uses `ttree.h` to intern DFA states by bitset key.
- Uses libdm pools, bitsets, logging, and allocation helpers from `libdm/misc/dmlib.h`.

Risk and edge cases:
- Matching mutates the compiled object by creating lazy states and filling transition tables, so a single `dm_regex` is not naturally immutable during first use.
- Pattern ordering matters: final numbers are assigned as target-transition charset leaves are encountered and `dm_regex_match()` returns `r - 1`.
- The generated combined regex depends on `snprintf()` into a pre-sized pool buffer; malformed user regexes fail during parsing.
- DFA state memory lives in the caller-supplied pool, while scratch structures also use that pool in this implementation, so freeing the pool invalidates the matcher.
- `dm_regex_match()` returns `-1` when no pattern matches.
- Fingerprinting is explicitly inefficient test code and forces all possible DFA transitions up front.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/matcher.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/parse_rx.c -->
# File Research: sources/block-storage/lvm2/libdm/regex/parse_rx.c

Purpose: parses libdm's small regex dialect into `rx_node` trees and performs a tree rewrite optimization that hoists common OR prefixes or suffixes.

Read coverage: complete file read, 683 lines.

Key responsibilities:
- Tokenizes regex input with support for character classes, negated classes, ranges, escapes, grouping, alternation, closures, `.` wildcard, `^`, and `$`.
- Represents literal tokens as 256-bit charset nodes and maps `^`/`$` to internal non-printable sentinels from `parse_rx.h`.
- Parses with recursive descent: term, closure term, concatenation, and OR expression.
- Allocates all parser state, charset bitsets, and nodes from a `dm_pool`.
- Implements optional DEBUG regex printing for inspecting generated trees.
- Optimizes alternations by finding common leftmost or rightmost CAT branches and converting forms like `(fa)|(fb)` into `f(a|b)`.
- Rotates nested OR nodes to expose common factors before exchange.
- Avoids considering charsets containing `TARGET_TRANS` as equal, preserving matcher-inserted pattern boundary markers.

Important entry points:
- `rx_parse_tok(struct dm_pool *mem, const char *begin, const char *end)`
- `rx_parse_str(struct dm_pool *mem, const char *str)`

Grammar and behavior:
- Closure operators `*`, `+`, and `?` apply repeatedly to the preceding term.
- Concatenation is implicit and right-recursive.
- Alternation is also parsed recursively with `|`.
- Character classes support escaped `n`, `r`, `t`, arbitrary escaped characters, and reversed ranges by swapping endpoints.
- `.` matches all nonzero bytes except newline and carriage return.

Dependencies:
- Includes `parse_rx.h`, which brings in libdm bitset/pool/logging helpers.
- Uses libdm allocation and bitset operations throughout.

Risk and edge cases:
- The parser is purpose-built, not a full POSIX/PCRE engine; unsupported regex syntax is either treated literally or rejected depending on token shape.
- Unterminated classes, incomplete ranges, trailing escapes, missing right parentheses, and malformed OR expressions return parse failure with log messages.
- Recursive parse and optimization passes can be deep for pathological regexes.
- The optimizer rewrites nodes in place using `memcpy()` over existing nodes, so tree ownership is pool-based and assumes no external node aliases.
- Comments note possible inefficiency and a FIXME about avoiding left/right OR rotation bouncing.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/parse_rx.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/parse_rx.h -->
# File Research: sources/block-storage/lvm2/libdm/regex/parse_rx.h

Purpose: declares the internal regex parse-tree representation and parser entry points used by the libdm matcher.

Read coverage: complete file read, 57 lines.

Key contents:
- Defines regex node types: `CAT`, `STAR`, `PLUS`, `OR`, `QUEST`, and `CHARSET`.
- Defines internal sentinel characters `HAT_CHAR`, `DOLLAR_CHAR`, and `TARGET_TRANS`.
- Declares `struct rx_node` with tree links, charset bitsets, DFA construction fields, and computed first/last/follow position bitsets.
- Declares `rx_parse_str()` and `rx_parse_tok()`.

Dependencies:
- Includes `libdm/misc/dmlib.h` for `dm_bitset_t`, pools, and related helpers.

Risk and edge cases:
- `TARGET_TRANS` is `'\0'`, so parser/matcher callers must respect explicit begin/end token parsing when NUL markers are embedded.
- The parse tree carries both AST and DFA-construction state, so the matcher mutates parser-produced nodes during compilation.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/parse_rx.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/ttree.c -->
# File Research: sources/block-storage/lvm2/libdm/regex/ttree.c

Purpose: implements a small ternary tree mapping fixed-length unsigned-integer key vectors to arbitrary data pointers.

Read coverage: complete file read, 118 lines.

Key responsibilities:
- Defines tree nodes with left, middle, and right links: left/right compare one key component, middle advances to the next key component.
- Creates `struct ttree` handles with a fixed key length and pool-backed allocation.
- Looks up keys by walking each key component through a binary-search branch, then descending through middle links.
- Inserts keys by creating missing component nodes and storing the supplied data pointer at the terminal node.

Important entry points:
- `ttree_create(struct dm_pool *mem, unsigned int klen)`
- `ttree_lookup(const struct ttree *tt, const unsigned int *key)`
- `ttree_insert(struct ttree *tt, const unsigned int *key, void *data)`

Dependencies:
- Uses `ttree.h` and libdm pool allocation helpers.

Risk and edge cases:
- `ttree_create()` rejects zero-length keys.
- Duplicate inserts replace terminal `data` without warning.
- No delete or rebalance exists; shape depends on key insertion order.
- The implementation casts away const in lookup to reuse pointer-to-pointer traversal.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/ttree.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/ttree.h -->
# File Research: sources/block-storage/lvm2/libdm/regex/ttree.h

Purpose: declares the internal fixed-length ternary-tree API used by libdm regex DFA state caching.

Read coverage: complete file read, 28 lines.

Key contents:
- Forward-declares opaque `struct ttree`.
- Declares create, lookup, and insert operations.
- Uses `unsigned int *` key vectors and untyped `void *` payloads.

Dependencies:
- Includes `libdm/misc/dmlib.h` for `struct dm_pool`.

Risk and edge cases:
- The API does not encode key length in calls after creation, so callers must provide keys matching the tree's configured `klen`.
- Payload lifetime is caller-owned; the tree only stores pointers.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/regex/ttree.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_parse.c -->
# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_parse.c

Purpose: provides shared token parsing helpers for libdm VDO status and stats parsers.

Read coverage: complete file read, 101 lines.

Key responsibilities:
- Skips ASCII whitespace over bounded string slices.
- Compares bounded tokens to NUL-terminated expected strings.
- Parses unsigned decimal tokens into `uint64_t` with empty-token, invalid-character, and overflow detection.
- Maps VDO operating-mode tokens to `enum dm_vdo_operating_mode`.

Important entry points:
- `vdo_parse_eat_space()`
- `vdo_parse_tok_eq()`
- `vdo_parse_uint64()`
- `vdo_parse_operating_mode()`

Dependencies:
- Includes `vdo/vdo_parse.h` and `libdm/misc/dmlib.h`.
- Uses `<ctype.h>` and `UINT64_MAX`.

Risk and edge cases:
- `vdo_parse_uint64()` zeroes the output on parse failure.
- Operating-mode parsing currently recognizes `recovering`, `read-only`, and `normal`.
- Token comparison requires exact length and content.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_parse.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_parse.h -->
# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_parse.h

Purpose: declares shared VDO parsing helper functions.

Read coverage: complete file read, 23 lines.

Key contents:
- Declares whitespace skipping, token equality, uint64 parsing, and operating-mode parsing helpers.
- Exposes bounded-token signatures using begin/end pointers.

Dependencies:
- Consumed by VDO status and stats parsing code.
- Does not include the enum-defining public header itself, so including compilation units must provide required type declarations before use.

Risk and edge cases:
- Function signatures use `void *context` for typed outputs in parser callbacks, so callers must pass correctly typed storage.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_parse.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_reader.c -->
# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_reader.c

Purpose: reads enough VDO on-disk metadata from a backend device or file to discover the VDO logical block count.

Read coverage: complete file read, 302 lines.

Key responsibilities:
- Defines packed VDO metadata structures for geometry blocks, headers, version numbers, volume geometry, region records, index config, and physical-volume component config.
- Decodes little-endian metadata fields into host order.
- Opens a VDO backend path, determines its size via `BLKGETSIZE64` or file `stat`, and reads the first 4 KiB metadata block.
- Validates the VDO magic string `dmvdo001`, geometry header id, and supported geometry major versions 4 and 5.
- Computes the VDO data-region offset from region start and bio offset, then seeks to the physical-volume component block.
- Reads component version/config data, rejects unknown major versions above 41, verifies nonce consistency, and returns logical block count.

Important entry point:
- `dm_vdo_parse_logical_size(const char *vdo_path, uint64_t *logical_blocks)`

Dependencies:
- Uses libdm logging helpers and endian conversion from `lib/mm/xlate.h`.
- Uses POSIX file APIs plus Linux `BLKGETSIZE64`.

Risk and edge cases:
- The parser is deliberately simplified and only extracts selected structure members.
- It assumes 4 KiB metadata block reads and packed layout compatibility with supported VDO versions.
- Short reads, invalid magic, unsupported versions, region offsets beyond file/device size, seek errors, and nonce mismatches all fail.
- On failure, `*logical_blocks` remains zero and the function returns `0`.
- Comments indicate it was based on VDO sources and may eventually be replaced by a library.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_reader.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_stats.c -->
# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_stats.c

Purpose: parses VDO kernel stats message strings into structured `dm_vdo_stats` data and, optionally, a flat list of label/value fields.

Read coverage: complete file read, 254 lines.

Key responsibilities:
- Parses nested VDO stats of the form `{ key : value, key : { nested : value } }`.
- Builds readable labels by joining nesting prefixes and converting camel-case keys to spaced labels.
- Recognizes selected labels and fills known `dm_vdo_stats` fields such as data/overhead/logical blocks, physical/logical block counts, block sizes, write bios, and operating mode.
- Optionally records up to `MAX_STATS` label/value pairs in `dm_vdo_stats_full.fields`.
- Allocates a single contiguous result containing `dm_vdo_stats_full`, optional field array, and `dm_vdo_stats`.

Important entry point:
- `dm_vdo_stats_parse(struct dm_pool *mem, const char *stats_str, unsigned flags)`

Dependencies:
- Uses `libdm/misc/dmlib.h`, public `libdm/libdevmapper.h` VDO stats structures, and helpers from `vdo/vdo_parse.h`.

Risk and edge cases:
- The parser is permissive: malformed sections generally stop traversal rather than returning an explicit parse error.
- Nesting deeper than 16 levels returns the end pointer and stops normal parsing.
- Full field collection is capped at 250 entries.
- Unknown fields are still preserved in full mode but ignored by structured stats extraction.
- If `DM_VDO_STATS_FULL` is not set, `field_count` is forced back to zero before return.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_status.c -->
# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_status.c

Purpose: parses VDO device-mapper target status strings into `struct dm_vdo_status`.

Read coverage: complete file read, 199 lines.

Key responsibilities:
- Parses a whitespace-separated VDO status line containing device, operating mode, recovering marker, index state, compression state, used blocks, and total blocks.
- Provides small enum parsers for compression state, recovering marker, and index state.
- Uses shared VDO parsing helpers for whitespace, token equality, operating mode, and uint64 fields.
- Stores human-readable parse failures in `dm_vdo_status_parse_result.error`.
- Supports allocation either from a supplied `dm_pool` or heap allocation.

Important entry point:
- `dm_vdo_status_parse(struct dm_pool *mem, const char *input, struct dm_vdo_status_parse_result *result)`

Dependencies:
- Includes public libdevmapper definitions unless built in the dmeventd plugin context.
- Uses `vdo/vdo_parse.h` and standard string/ctype/varargs helpers.

Risk and edge cases:
- The parser requires exactly the expected token count and rejects extra trailing tokens.
- On heap-backed failure it frees the duplicated device string and status object; pool-backed failed allocations remain pool-owned.
- Unknown operating/index/compression tokens produce explicit parse errors.
- The recovering field accepts only `recovering` or `-`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_status.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_target.c -->
# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_target.c

Purpose: validates VDO target parameter ranges before constructing or loading VDO device-mapper targets.

Read coverage: complete file read, 162 lines.

Key responsibilities:
- Validates minimum I/O size, block map cache size, block map era length, index memory size, slab size, max discard, VDO thread counts, write policy, and logical VDO size.
- Enforces that hash-zone, logical, and physical thread counts are either all zero or all nonzero.
- Logs specific errors for every invalid parameter while continuing validation to report multiple problems.
- Returns a boolean-like aggregate validity result.

Important entry point:
- `dm_vdo_validate_target_params(const struct dm_vdo_target_params *vtp, uint64_t vdo_size)`

Dependencies:
- Includes `libdm/misc/dmlib.h`, which supplies public VDO target parameter constants and logging.

Risk and edge cases:
- Validation depends on public constant ranges staying synchronized with kernel target expectations.
- `vdo_size` is in sectors; error formatting converts the maximum to TiB and excess to KiB.
- Unknown write-policy enum values are treated as internal errors.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/vdo/vdo_target.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/Makefile.in -->
# File Research: sources/block-storage/lvm2/tools/Makefile.in

Purpose: defines the Autotools make rules for building, generating, and installing LVM2 command-line tools and the `liblvm2cmd` command library.

Read coverage: complete file read, 222 lines.

Key responsibilities:
- Lists primary tool source files and auxiliary command-library/man-generator sources.
- Defines build targets for `lvm`, `lvm.static`, `liblvm2cmd.a`, `liblvm2cmd-static.a`, shared `liblvm2cmd`, and `man-generator`.
- Includes project-wide `make.tmpl` and cflow inputs.
- Generates `.commands` from `cmdnames.h`/`commands.h` by preprocessing and filtering internal/deprecated command names.
- Generates `command-count.h` by counting `ID:` records in `command-lines.in`.
- Generates `command-lines-input.h` by embedding non-comment, non-separator command definition lines as NUL-separated C string data.
- Hooks generated command metadata into object and dependency builds.
- Installs dynamic/static tools, command-library headers, shared libraries, and symlinks for individual LVM commands.

Dependencies:
- Relies on configure substitutions such as `@srcdir@`, `@STATIC_LINK@`, `@SHARED_LINK@`, `@CMDLIB@`, compiler/linker variables, and install paths.
- Depends on `command-lines.in`, `cmdnames.h`, `commands.h`, `license.inc`, and the wider LVM internal libraries.

Risk and edge cases:
- Command metadata generation strips comments, separators, and empty lines, so syntax-significant content must not look like those forms.
- `.commands` is produced by C preprocessor expansion of macro-based command name data, then filtered with a hard-coded exclusion list.
- Static/dynamic installation depends on configure options and may install different target sets.
- `liblvm2cmd.a` is assembled by copying `liblvm-internal.a` then adding objects, which is unusual but intentional for this build.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/args.h -->
# File Research: sources/block-storage/lvm2/tools/args.h

Purpose: provides the X-macro catalogue of LVM command-line options, including option IDs, short names, long names, value types, flags, grouping behavior, and help/man text.

Read coverage: complete file read, 1,897 lines.

Key responsibilities:
- Defines every recognized LVM tool option through repeated `arg(id, short, long, val_type, flags, groupable_count, help)` macro invocations.
- Places long-only options first, then synonym-only aliases, then short-option definitions, with `ARG_UNUSED` at the start and `ARG_COUNT` at the end.
- Captures detailed help text for command-specific and shared options, with `#command` markers used to vary descriptions by command.
- Marks countable options such as `--debug`, `--verbose`, `--quiet`, and force variants.
- Marks groupable options such as tags, devices, settings, report options, and PV-specific RAID options.
- Defines synonyms such as `--allocation`, `--available`, `--corelog`, raid-prefixed aliases, `--split`, and `--virtualoriginsize`.
- Covers general configuration/reporting options, activation and locking, devices file management, PV/VG/LV metadata, RAID, thin, cache, writecache, integrity, VDO, filesystem resize, persistent reservations, and deprecated options.
- Documents options whose value parser is overridden per command, notably `--size` and `--extents`.

Dependencies:
- Consumed by code that defines the `arg` macro to generate enums, lookup tables, parsing metadata, and documentation.
- Value type names refer to parser definitions in the tools value layer, such as `bool_VAL`, `sizemb_VAL`, `pv_VAL`, `segtype_VAL`, and VDO/cache/thin-specific values.

Risk and edge cases:
- This file is data-as-code: macro argument order and sentinel placement are part of the parser contract.
- Short option characters are reused by different logical options; command definitions disambiguate valid usage.
- Synonym options intentionally have no generated help text and must translate to standard option IDs before command matching.
- Some entries are marked not used or deprecated but remain for compatibility.
- Help strings include roff escapes and command-specific fragments, so formatting changes can affect generated man/help output.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/args.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/cmdnames.h -->
# File Research: sources/block-storage/lvm2/tools/cmdnames.h

Purpose: extracts command names from `commands.h` through macro redefinition.

Read coverage: complete file read, 18 lines.

Key contents:
- Defines `xx(a, b, ...) a`.
- Includes `commands.h`, causing each command macro record to expand to its command-name token.

Dependencies:
- Used by the tools Makefile to preprocess command names into `.commands`.
- Requires `commands.h` to define records using the expected `xx` macro shape.

Risk and edge cases:
- This file only works in preprocessing contexts where token output is the desired product.
- Changes to `commands.h` macro signatures would require updating the `xx` definition.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/cmdnames.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/command-lines.in -->
# File Research: sources/block-storage/lvm2/tools/command-lines.in

Purpose: declaratively defines LVM command syntaxes, common option groups, optional/required arguments, command IDs, descriptions, inferred types, implicit options, and validation rules.

Read coverage: complete file read, 2,158 lines.

Key responsibilities:
- Documents the command-definition grammar used by the LVM command parser and help/man generator.
- Defines common option groups such as `OO_ALL`, `OO_REPORTING`, `OO_REPORT`, `OO_CONFIG`, and command-family groups for lvchange, lvconvert, lvcreate, vgchange, and others.
- Describes how required options, optional options (`OO:`), optional positional arguments (`OP:`), ignored/internal options (`IO:`), command IDs, descriptions, rules, flags, and `AUTOTYPE` annotations work.
- Encodes command families for `lvchange`, `lvconvert`, `lvcreate`, `lvdisplay`, `lvextend`, `lvmconfig`, `lvmdevices`, `lvreduce`, `lvremove`, `lvrename`, `lvresize`, `lvs`, `lvscan`, PV commands, VG commands, reports, built-ins, and deprecated commands.
- Captures many historical/secondary syntaxes through `FLAGS: SECONDARY_SYNTAX` and `FLAGS: PREVIOUS_SYNTAX`.
- Uses `RULE:` lines to reject invalid option combinations, LV types, and LV properties after command matching.
- Uses `AUTOTYPE:` to document or validate inferred segment types without making `--type` part of the matching key.
- Assigns stable `ID:` strings that map syntactic variants to implementation handlers and command counts.

Major command areas:
- LV conversion definitions cover RAID/mirror type conversions, split/merge flows, thin/cache/writecache/VDO pool conversion, cache attach/detach, metadata swap, repair/replace, polling, and RAID integrity.
- LV creation definitions cover linear, striped, mirror, RAID, COW snapshots, thin pools, thin volumes, cache pools, cache/writecache attach flows, and VDO volumes.
- PV/VG command definitions cover creation, resize, metadata repair/check, devices file management, activation, locking, persistent reservations, import/export, split/merge/reduce/remove/rename, reports, and display variants.
- Built-in/deprecated definitions preserve compatibility for aliases such as `config`, `dumpconfig`, `pvdata`, `vgconvert`, `lvmdiskscan`, `lvmsadc`, and `lvmsar`.

Dependencies:
- Option names must correspond to canonical entries in `args.h`, with documented synonym translation.
- Value types must correspond to parser types in `tools/vals.h`.
- `Makefile.in` embeds this file into `command-lines-input.h` and counts `ID:` lines for `command-count.h`.
- Runtime command parsing and generated documentation rely on this declarative data.

Risk and edge cases:
- The file explicitly documents ambiguous syntaxes where command matching cannot distinguish LV types before metadata is read.
- Some validations cannot be expressed in command definitions and are deferred to command implementations.
- Order matters where ambiguous definitions could match the same user input.
- Comments note inconsistent historical behavior for thin/cache/type variants, making regression risk high when editing.
- `--size`/`--extents` alternation and lvcreate VG/name inference are handled automatically outside the literal definitions.
- Generated command input omits comments, separators, and blank lines; only definition lines affect runtime metadata.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/command-lines.in -->