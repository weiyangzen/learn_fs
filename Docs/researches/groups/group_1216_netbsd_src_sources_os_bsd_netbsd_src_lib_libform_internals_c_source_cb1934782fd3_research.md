# Group Research: group_1216_netbsd_src_sources_os_bsd_netbsd_src_lib_libform_internals_c_source_cb1934782fd3

Scope: `Docs/research_subset_a.md`; all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/internals.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/internals.c

Core implementation for NetBSD `libform` field editing internals. It manages field line lists, cursor state, tab expansion metadata, wrapping, curses redraw, field/page traversal, validation dispatch, and driver request handling.

Important responsibilities:
- Maintains `_FORMI_FIELD_LINES` linked lists, including free-list reuse, row copying, row destruction, line splitting, line joining, and hard-return propagation.
- Implements reversible word wrapping in `_formi_wrap_field`, backing up affected rows before mutating so failed wraps can restore prior state.
- Handles cursor movement and editing requests in `_formi_manipulate_field`, including char/line/word movement, insert/delete, clear-to-EOL/EOF/field, overlay/insert mode, and vertical/horizontal scrolling.
- Draws fields with curses in `_formi_redraw_field` and `_formi_draw_page`, applying field visibility/public/private behavior, foreground/background attributes, padding, justification, and tab expansion.
- Computes form page metadata, sorted field traversal order, and directional neighbors through `_formi_find_pages`, `_formi_sort_fields`, and `_formi_stitch_fields`.
- Dispatches character and full-field validation through linked `FIELDTYPE` chains and synchronizes editable line state back to buffer 0 via `_formi_sync_buffer`.

Notable implementation details:
- Tabs are treated as 8-column stops and cached in per-row `_formi_tab_t` lists.
- Single-line dynamic fields horizontally scroll; multiline fields scroll vertically and wrap.
- Validation honors `O_NULLOK`, `O_PASSOK`, `O_STATIC`, `O_WRAP`, `O_BLANK`, and type callbacks.
- The code is stateful and pointer-heavy; cursor fields such as `row_xpos`, `cursor_xpos`, `start_char`, `cursor_ypos`, `cur_line`, and `start_line` must remain consistent after edits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/internals.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/internals.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/internals.h

Internal header for NetBSD `libform`. It defines shared constants, internal data structures, and prototypes used across the library’s form editor and type implementations.

Key contents:
- Direction constants `_FORMI_BACKWARD` and `_FORMI_FORWARD`.
- `DEFAULT_FORM_OPTS`, combining visible/active/public/edit/wrap/blank/autoskip/nullok/passok/static defaults.
- `FIELDTYPE` internal flag bits: `_TYPE_HAS_ARGS`, `_TYPE_IS_LINKED`, `_TYPE_IS_BUILTIN`, and `_TYPE_HAS_CHOICE`.
- Internal page descriptor, tab-stop descriptor, and field-line structures.
- Prototypes for field editing, drawing, wrapping, tab calculation, field traversal, validation, and buffer sync helpers.

This file is the private contract between `internals.c`, posting logic, and builtin field type validators.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/internals.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/post.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/post.c

Implements public form posting and unposting.

`post_form` validates arguments and state, checks field connection, scales the form against the target window, runs form and field init hooks, positions the first field, draws the current page, marks the form posted, and positions the cursor.

`unpost_form` checks state, runs field and form termination hooks, clears the form window, and clears the posted flag.

Behavior is tightly coupled to `internals.c` for first-field positioning and page drawing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/post.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/std_header.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/std_header.c

Minimal source file containing only the common copyright/license block, `<sys/cdefs.h>`, and NetBSD `__RCSID`.

It appears to exist as a standard compilation/header identity unit rather than implementing behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/std_header.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_alnum.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/type_alnum.c

Defines builtin `TYPE_ALNUM`.

It stores one argument, `width`, and validates that a field buffer contains a non-empty alphanumeric token, surrounded only by spaces or tabs, whose length does not exceed `width`. On successful field validation it normalizes buffer 0 to the trimmed token.

Character validation accepts `isalnum` characters only. The builtin `FIELDTYPE` has argument lifecycle callbacks and no choice callbacks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_alnum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_alpha.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/type_alpha.c

Defines builtin `TYPE_ALPHA`.

It mirrors `TYPE_ALNUM` but accepts alphabetic characters only. The field validator trims leading/trailing blanks, rejects empty input, checks that the alphabetic span is no longer than the configured width, rejects any non-blank trailing data, and writes the normalized value back to buffer 0.

Character validation uses `isalpha`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_alpha.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_enum.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/type_enum.c

Defines builtin `TYPE_ENUM`.

Arguments are a null-terminated choices array plus `ignore_case` and `exact` flags. The implementation counts choices at argument creation and uses `match_enum` to compare trimmed field input against trimmed choices.

Field validation replaces buffer 0 with the matched canonical choice. Choice callbacks implement wraparound next/previous selection using the current field buffer. Matching supports exact-length mode or prefix-style mode depending on `exact`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_enum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_integer.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/type_integer.c

Defines builtin `TYPE_INTEGER`.

Arguments include `precision`, `min`, and `max`. Field validation accepts optional leading sign, digits, and trailing blanks, converts via `atol`, enforces the configured range when `min <= max`, then rewrites buffer 0 with `asprintf("%.*ld", precision, number)`.

Character validation accepts digits, `+`, and `-`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_integer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_ipv4.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/type_ipv4.c

Defines builtin `TYPE_IPV4`.

Field validation accepts three input styles:
- dotted quad: `a.b.c.d`
- classless/CIDR: `a.b.c.d/mask`
- hex: `0xaabbccdd`

It parses components, checks octets are <= 255 and masks <= 32, then normalizes buffer 0 to the input style’s canonical representation. If buffer 1 exists, it stores dotted-quad form there regardless of input style.

Character validation accepts hex digits, `.`, `x`/`X`, and `/`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_ipv4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_ipv6.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/type_ipv6.c

Defines builtin `TYPE_IPV6`.

Field validation uses `getaddrinfo` with `AF_INET6` and `AI_NUMERICHOST` to require a numeric IPv6 literal, rejects results with multiple addresses, then formats the address with `getnameinfo(..., NI_NUMERICHOST)` and writes the normalized text to buffer 0.

Character validation accepts hex digits, `.`, and `:`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_ipv6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_numeric.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/type_numeric.c

Defines builtin `TYPE_NUMERIC`.

Arguments include `precision`, `min`, and `max`. Field validation accepts signed decimal/scientific notation, optional fractional part, optional exponent, and trailing blanks. It converts with `atof`, range-checks when `min < max`, and normalizes buffer 0 using fixed decimal formatting with the configured precision.

Character validation accepts digits, signs, `.`, `e`, and `E`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_numeric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_regex.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libform/type_regex.c

Defines builtin `TYPE_REGEXP`.

Argument creation compiles the supplied expression with `regcomp` using `REG_EXTENDED | REG_NOSUB | REG_NEWLINE`. Copies share the compiled regex by incrementing a reference count. Free decrements the count and frees storage at zero.

Field validation runs `regexec` against the field buffer. There is no character-level validation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libform/type_regex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/Makefile

Build file for NetBSD `libintl`.

It builds library `intl` from gettext, textdomain, iconv conversion, dummy GNU-compat symbol, string hash, sysdep support, and plural parser sources. It installs `libintl.h` to `/usr/include` and wires `gettext.3` manual links for gettext, plural gettext, domain binding, textdomain, and codeset APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/gettext.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/gettext.c

Main implementation of NetBSD `libintl` gettext lookup.

Key behavior:
- Provides gettext/dgettext/dcgettext/ngettext/dngettext and context-aware pgettext variants.
- Looks up locale paths from `LANGUAGE`, `LC_ALL`, category-specific env vars, or `LANG`, with locale fallback splitting.
- Locates `.mo` files under bound textdomain directories and maps them with `mmap`.
- Validates GNU `.mo` headers, flips endian fields, builds host-order original/translation tables, optional hash tables, charset metadata, and plural parser state.
- Supports `.mo` revisions with system-dependent strings and expands sysdep records into hash lookup.
- Looks up translations through hash table first, binary search second.
- Applies plural expression results to NUL-separated plural translation strings.
- Converts translation encoding through `__gettext_iconv` unless translating the empty header string.
- Falls back to original singular/plural message on failure.

State is cached by last domain/category/language path and per-domain binding mappings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/gettext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/gettext_dummy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/gettext_dummy.c

Provides the global symbol `_nl_msg_cat_cntr`.

The comment explains this is a compatibility hack for GNU gettext’s autoconf macro checks, causing software to treat NetBSD `libintl` sufficiently like GNU gettext so `.mo` files install under `/usr/share/locale` rather than `/usr/lib/locale`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/gettext_dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/gettext_iconv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/gettext_iconv.c

Implements translation charset conversion for gettext results.

`__gettext_iconv` compares the `.mo` charset against the bound codeset or current locale `CODESET`. If conversion is needed, it uses `iconv_open`, `iconv`, and a static allocation arena. Converted messages are cached by original message pointer in a `tsearch` tree.

Important constraints:
- Returned converted buffers are intentionally never freed due to gettext API lifetime expectations.
- Cache key compares original message pointers, not string contents.
- Locking is marked as TODO with `XXX LOCK` comments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/gettext_iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/libintl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/libintl.h

Public `libintl` header.

Declares gettext, domain-specific gettext, plural gettext, context-aware pgettext variants, `textdomain`, `bindtextdomain`, and `bind_textdomain_codeset`. It also defines expression macros for pgettext-style helpers unless included through GNU gettext’s compatibility header.

Uses NetBSD `__format_arg` annotations to preserve format-string checking through translated strings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/libintl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/libintl_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/libintl_local.h

Private `libintl` header defining GNU `.mo` file structures and host-side runtime structures.

Includes:
- Magic constants, revision helpers, default domain name, mmap size limit.
- Packed on-disk `.mo`, entry, sysdep segment, and sysdep string structures.
- Host-side converted structures for string tables, plural metadata, charset, hash table, and sysdep data.
- `mohandle` and `domainbinding` structures.
- Globals for domain bindings and current domain.
- Internal prototypes for iconv conversion, gettext string hashing, and sysdep tag expansion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/libintl_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/pathnames.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/pathnames.h

Defines the default gettext textdomain path:

`_PATH_TEXTDOMAIN` is `/usr/share/locale`.

Used by `textdomain.c` and `gettext.c` for default domain binding and implicit domain setup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/plural_parser.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/plural_parser.c

Hand-written tokenizer, recursive-descent parser, AST manager, and evaluator for gettext `Plural-Forms:` headers.

Supported expression grammar includes:
- identifiers, constants, parentheses
- unary `!`
- multiplicative, additive, relational, equality, logical AND/OR
- ternary conditional `?:`

The parser extracts `Plural-Forms:`, parses `nplurals=...;`, parses `plural=...;`, and returns an AST plus plural count. Runtime evaluation calculates the plural index for a given `n`.

Only identifier `n` is accepted in normal builds. Test builds can allow empty expressions and arbitrary identifiers. Public internal entry points are `_gettext_parse_plural`, `_gettext_calculate_plural`, and `_gettext_free_plural`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/plural_parser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/plural_parser.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/plural_parser.h

Private header for the gettext plural parser.

Forward-declares `struct gettext_plural` and exposes:
- `_gettext_parse_plural`
- `_gettext_calculate_plural`
- `_gettext_free_plural`

Used by `gettext.c` to parse `.mo` headers and compute plural translation indexes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/plural_parser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/strhash.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/strhash.c

Implements `__intl_string_hash`, the PJW-style hash used for gettext `.mo` hash-table lookup.

The function shifts the hash by four bits per byte, adds the byte, folds high bits, and returns a 32-bit hash. It is derived from NetBSD Citrus database hash code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/strhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/sysdep.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/sysdep.c

Provides system-dependent gettext string expansion support.

It defines a sorted table mapping `inttypes.h` printf/scanf macro names, such as `PRId64` and `SCNxPTR`, to their platform-specific string expansions. `__intl_sysdep_get_string_by_tag` uses `bsearch` to resolve a tag and returns the expansion plus length, or an empty string if unknown.

Used by `.mo` sysdep string expansion in `gettext.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/sysdep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/textdomain.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libintl/textdomain.c

Implements gettext domain binding state.

Key behavior:
- Initializes default binding for domain `messages` at `/usr/share/locale`.
- `textdomain` gets/sets current default domain, with empty string resetting to default.
- `bindtextdomain` creates or updates a per-domain locale path and invalidates the current mapping.
- `bind_textdomain_codeset` stores a per-domain output codeset.
- Domain bindings are kept in a simple linked list headed by `__bindings`.

This file owns `__current_domainname`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libintl/textdomain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libipsec/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libipsec/Makefile

NetBSD build file for `libipsec`, sourced from imported `crypto/dist/ipsec-tools`.

It builds policy and PF_KEY helpers, parser/lexer sources, and debug support. It enables Fortify for a network protocol library, shared-lib install directory behavior, `IPSEC_DEBUG`, and conditional `INET6`. It sets yacc/lex prefixes to avoid symbol collisions and installs `ipsec_set_policy.3` links.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libipsec/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libipsec/config.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libipsec/config.h

Generated configuration header for NetBSD’s ipsec-tools build.

It enables major ipsec-tools features including admin port, dead peer detection, IKE fragmentation, hybrid authentication, NAT traversal, NAT-T draft 02, NAT-T RFC support, advanced IPv6 API, and SHA2 support.

It records available headers/functions, OpenSSL headers, PAM/RADIUS function availability, package identity/version, signal handler type, ANSI/POSIX header support, `va_copy`, `YYTEXT_POINTER`, and defines `PATH_IPSEC_H` as `<netipsec/ipsec.h>`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libipsec/config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libipsec/package_version.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libipsec/package_version.h

Small package identity header for imported ipsec-tools.

Defines package name as `ipsec-tools`, version as `cvs`, package string as `ipsec-tools cvs`, and project URL as `http://ipsec-tools.sourceforge.net`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libipsec/package_version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/Makefile

Build file for NetBSD `libisns`.

It builds `isns` from core, PDU, socket I/O, task, thread, utility, and file I/O sources. Installs `isns.h` and `isns_defs.h` to `/usr/include`, links with pthread, sets warning level 5, and suppresses string truncation warnings for `isns.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns.c

Public lifecycle and connection setup implementation for `libisns`.

Functions:
- `isns_init` allocates config, creates a control pipe, creates a kqueue, registers pipe events, initializes buffer pools, starts the control thread, and returns an opaque handle.
- `isns_add_servercon` deep-copies an `addrinfo`, creates an init-socket task, queues it, signals processing, and waits for task completion.
- `isns_init_reg_refresh` creates a refresh task for a node and interval.
- `isns_stop` issues stop, destroys the thread/config, and destroys buffer pools.

The implementation is task-queue driven and hides internal config behind `ISNS_HANDLE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns.h

Public `libisns` API header.

Defines opaque `ISNS_HANDLE` and `ISNS_TRANS` types, invalid handle constants, TLV iteration constants, and public functions for:
- library init/stop
- adding server connections
- starting registration refresh
- creating/freeing/sending transactions
- adding and retrieving TLVs
- adding string TLVs

The API exposes protocol transactions while keeping implementation details private.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_config.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_config.h

Private configuration header for `libisns`.

Defines debug macro `DBG`, includes internal modules, defines mutex type constants, and declares `struct isns_config_s`.

The config structure tracks:
- kqueue and control pipe descriptors
- control thread pointer
- socket state and address info
- current input PDU
- task queue mutex/current task/queue head
- transaction mutex
- server/client mode flag
- registration refresh state

Also provides `isns_is_socket_init_done`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_defs.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_defs.h

Protocol definition header for iSNS.

Defines:
- iSNS function IDs for registration, query, deregistration, SCN, discovery domain operations, ESI, heartbeat, iFCP requests, and response IDs.
- iSNS tag type IDs for entity, portal, iSCSI node, portal group, Fibre Channel, switch, discovery domain set, and discovery domain attributes.
- PDU header flag constants for first/last PDU, replace registration, authentication, sender server, and sender client.

This is the public constants surface for constructing and interpreting iSNS PDUs/TLVs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_defs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_fileio.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_fileio.c

Thin file I/O wrappers for vector I/O.

`isns_file_writev` calls either `wepe_sys_writev` when `HAVE_WEPE` is enabled or plain `writev`. `isns_file_readv` does the same for read side with `readv`.

These wrappers isolate platform-specific WEPE support from the rest of `libisns`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_fileio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_fileio.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_fileio.h

Private header for `libisns` vector I/O wrappers.

Includes errno/types/uio headers and declares:
- `isns_file_writev`
- `isns_file_readv`

Used by internal socket/file transport code through `isns_config.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_fileio.h -->