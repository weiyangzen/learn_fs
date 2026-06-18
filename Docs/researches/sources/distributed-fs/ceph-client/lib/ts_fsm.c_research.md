<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_fsm.c -->
# sources/distributed-fs/ceph-client/lib/ts_fsm.c

## Purpose
Finite-state-machine textsearch algorithm that matches tokenized patterns over streamed byte blocks, supporting specific bytes, ctype-like token classes, wildcards, optional/multiple recurrence, and an optional head-ignore mode.

## APIs, Types, and Functions
Defines private `struct ts_fsm` with token count and copied `struct ts_fsm_token` array. `token_map` translates public token type IDs into ctype bitmasks, and `token_lookup_tbl[256]` classifies bytes. Core functions are `match_token()`, `fsm_find()`, `fsm_init()`, `fsm_get_pattern()`, and `fsm_get_pattern_len()`. `fsm_ops` registers algorithm name `"fsm"`.

## Control Flow, State, and Persistence
`fsm_init()` validates that pattern length is an integral nonzero token array, rejects `TS_IGNORECASE`, validates token type and recurrence limits, permits `TS_FSM_HEAD_IGNORE` only as a non-final first token, allocates config storage, copies tokens, and maps token types to bitmasks. `fsm_find()` reads blocks via `get_next_block()`, maintains consumed byte count and block index, determines strict mode from the first token, and walks tokens applying recurrence rules. Mismatches either fail in strict mode or advance and restart in non-strict mode. On a match, it updates `state->offset` to the end and returns the match start.

## Dependencies and Integration
Depends on textsearch core, `linux/textsearch_fsm.h`, module registration, and ctype constants. It integrates as an algorithm selectable by `textsearch_prepare("fsm", ...)`.

## Risks and Test Signals
Risks include complex block-boundary control flow, unsupported ignore-case mode, potential allocation-size overflow because `sizeof(*fsm) + len` is not explicitly checked, and assumptions encoded in the manual 256-entry classification table. Test signals should include strict and non-strict matches, every recurrence type, token classes near ASCII/non-ASCII boundaries, block splits at every token boundary, invalid token validation, and final-token multi/any behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_fsm.c -->
