# sources/distributed-fs/openafs/src/external/heimdal/krb5/config_file.c

Purpose: implements Heimdal krb5 configuration parsing, tree storage, typed lookup helpers, and cleanup for text configuration files, string-backed deprecated parsing, and Apple plist configuration.

Important APIs/types/functions: `struct fileptr` abstracts `FILE *` versus string input. `_krb5_config_get_entry()` creates or finds `krb5_config_binding` nodes. Parser internals are `config_fgets()`, `parse_section()`, `parse_binding()`, `parse_list()`, and `krb5_config_parse_debug()`. Public entry points include `krb5_config_parse_file_multi()`, `krb5_config_parse_file()`, `krb5_config_file_free()`, `_krb5_config_get_next()`, `_krb5_config_vget_next()`, `krb5_config_get_list()`, `krb5_config_get_string()`, `krb5_config_get_strings()`, bool/time/int getters, and deprecated `krb5_config_parse_string_multi()`.

Control flow: text parsing reads lines, strips CR/LF, skips comments and blank lines, opens top-level `[section]` nodes, and parses `name = value` or `name = { ... }` bindings recursively until a matching `}`. Lookup walks variadic path components through list nodes and can continue from a previous binding pointer to return repeated values.

State and persistence behavior: parsing allocates a linked tree of config bindings and strings that persists until `krb5_config_file_free()`. Multi-parse appends into an existing tree. Returned strings are borrowed from that tree. Apple plist parsing converts CoreFoundation dictionaries into the same tree.

Dependencies and integration points: uses `krb5_locl.h`, krb5 error-message APIs, `issuid()`, passwd/home expansion, optional `_krb5_expand_path_tokens()`, and optional CoreFoundation. It feeds `context->cf` lookup callers throughout the Kerberos library.

Risks: malformed braces and missing `=` produce parser errors with line numbers, but duplicate names are appended and lookup order matters. Home directory expansion is security-sensitive and gated by `_krb5_homedir_access()` and `issuid()`. `_krb5_config_copy()` does not fully unwind partial allocation failures. `next_component_string()` mutates copies in place and has quote parsing edge cases.

Test signals: useful coverage includes config files with repeated keys, nested lists, comments, unmatched braces, bindings before sections, `~/` expansion under setuid-like conditions, plist parsing on Apple builds, and typed getter defaults.
