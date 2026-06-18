# sources/distributed-fs/ceph-client/security/apparmor/include/match.h

## Purpose
`match.h` defines the packed DFA table format and matching API used by AppArmor policy databases for paths, labels, network rules, capabilities, and transition parsing.

## Important APIs and types
Core constants include `DFA_NOMATCH`, `DFA_START`, `YYTH_MAGIC`, table IDs, data-width flags, accept flags, and match flags. `struct table_set_header`, `struct table_header`, and `struct aa_dfa` describe loaded DFA tables. Public functions include `aa_dfa_unpack`, `aa_dfa_match_len`, `aa_dfa_match`, `aa_dfa_next`, `aa_dfa_outofband_transition`, match-until helpers, `aa_dfa_leftmatch`, and refcount helpers.

## Control flow and integration
Policy unpack loads big-endian packed tables, converts to host order with `UNPACK_ARRAY`, and produces refcounted `aa_dfa` objects. Mediation code then starts from class-specific states and consumes strings, bytes, NUL separators, or out-of-band transitions to reach accept table entries that map to permissions.

## State and persistence
DFAs are in-memory policy objects with kref-managed lifetime and pointers to individual table headers. The packed input format is a policy ABI between userspace parser and kernel.

## Dependencies
It depends on kref and AppArmor policy unpack/match implementations. `ACCEPT_TABLE` and related macros require expected table IDs to be present.

## Risks
Malformed DFA tables are security sensitive. Endianness conversion, table sizes, out-of-band transitions, and accept table indexing must be verified during unpack. `aa_state_t` is an unsigned int, so table bounds and state validation matter.

## Test signals
KUnit/fuzz tests should cover DFA unpack validation, invalid magic/flags/table widths, endian conversion, normal matches, leftmost matches, NUL transitions, out-of-band transitions, and refcount cleanup.
