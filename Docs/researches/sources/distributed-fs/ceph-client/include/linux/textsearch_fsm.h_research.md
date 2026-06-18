<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/textsearch_fsm.h -->
# sources/distributed-fs/ceph-client/include/linux/textsearch_fsm.h

## Purpose
defines token types, recursion limits, and token layout for the finite-state-machine textsearch algorithm.

## Important APIs, Types, and Functions
The file is 50 lines and exports these visible symbol families: types/enums `ts_fsm_token`; macros/constants `TS_FSM_TYPE_MAX`, `TS_FSM_RECUR_MAX`; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
FSM parser/compiler code builds `ts_fsm_token` arrays with value, type, repetition, recursion, and next-token offset. Runtime matching interprets these tokens to consume literal values, wildcard classes, alternation, and control tokens.

## State and Persistence Behavior
Compiled token arrays are algorithm-private configuration state owned by textsearch configs.

## Dependencies and Integration Points
It depends only on kernel types and is consumed by the FSM textsearch implementation. Direct includes are `linux/types.h`.

## Risks and Edge Cases
Token recursion and repetition limits protect against unbounded matching. Bad `next` offsets or type values can make the matcher skip tokens or overrun compiled patterns.

## Test Signals
Compile valid and invalid FSM patterns, cover recursion/repetition boundaries, fuzz token streams, and compare matches against expected pattern-language behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/textsearch_fsm.h -->
