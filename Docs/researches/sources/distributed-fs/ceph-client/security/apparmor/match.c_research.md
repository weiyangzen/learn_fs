# sources/distributed-fs/ceph-client/security/apparmor/match.c

Purpose: implements AppArmor's serialized DFA unpacker, verifier, matcher, out-of-band transitions, accept-until matching, and leftmatch fallback.

Important APIs/functions: `aa_dfa_unpack()` parses table-set headers and tables; `verify_table_headers()` and `verify_dfa()` validate sizes, bounds, diff-encoding chains, and OOB transition flags; `aa_dfa_free_kref()` frees tables; `aa_dfa_match_len()`, `aa_dfa_match()`, `aa_dfa_next()`, `aa_dfa_outofband_transition()`, `aa_dfa_match_until()`, `aa_dfa_matchn_until()`, and `aa_dfa_leftmatch()` perform runtime matching.

Control flow: unpack reads big-endian table metadata, validates accepted table data widths, remaps 16-bit transition tables to 32-bit, optionally verifies all transitions, then exposes compact default/base/next/check tables. Matching uses optional equivalence classes and a default-chain loop to transition for each byte.

State and persistence: a DFA owns kvallocated tables and a kref. Loaded profile policy DBs, `nulldfa`, and `stacksplitdfa` hold references.

Dependencies and integration: all policy classes use this engine through policy DB start states and permission lookup. Risks include malformed policy blobs, integer bounds around `base_idx + 255`, diff-encoding loops, OOB `-1` transition indexing, vmalloc alias synchronization, and accepting unverified states. Test with valid/invalid packed DFAs, 16-bit remap, EC tables, diff encoded chains, OOB transitions, null transitions, and policy fuzzing.
