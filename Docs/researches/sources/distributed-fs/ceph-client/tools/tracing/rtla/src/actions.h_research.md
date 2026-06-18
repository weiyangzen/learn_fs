# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/actions.h

## Purpose
`actions.h` defines the data structures and public API for RTLA threshold/end actions.

## Important APIs, Types, and Functions
`enum action_type` enumerates `ACTION_TRACE_OUTPUT`, `ACTION_SIGNAL`, `ACTION_SHELL`, and `ACTION_CONTINUE`. `struct action` stores type-specific data in a union. `struct actions` stores the dynamic action list, length/capacity, presence flags, a `continue_flag`, and the `trace_output_inst` external dependency used for saving trace buffers. The `for_each_action` macro iterates actions. Prototypes expose initialization, destruction, action additions, parsing, and execution.

## Control Flow and Integration
The header contains no runtime logic but is consumed by parsers in osnoise/timerlat modes and by `common_threshold_handler()`/end-of-run handling. `trace_output_inst` is filled in `run_tool()` when trace-output actions require an auxiliary trace instance.

## State and Persistence
The action list owns duplicated string data and can trigger persistent trace files or external side effects when performed.

## Dependencies and Integration Points
The header includes tracefs for `struct tracefs_instance` and `<stdbool.h>`. It is included by `common.h`, which places action sets in `struct common_params`.

## Risks and Edge Cases
The union layout requires callers to respect `type` before reading fields. `present[]` and `continue_flag` are part of runtime behavior and must be initialized consistently. `action_default_size` is a header-level `static const int`, giving each translation unit its own copy.

## Test Signals
Compile all action users, verify presence flags are set for each add function, and test trace-output actions with and without a valid `trace_output_inst`.
