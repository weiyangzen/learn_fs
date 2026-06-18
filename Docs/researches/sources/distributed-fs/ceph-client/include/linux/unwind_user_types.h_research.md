<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_user_types.h -->
# sources/distributed-fs/ceph-client/include/linux/unwind_user_types.h

Purpose: defines generic user-stack unwinding data structures and type-selection flags.

Important APIs and types: `enum unwind_user_type_bits` currently defines frame-pointer unwinding as the first priority bit. `enum unwind_user_type` provides `UNWIND_USER_TYPE_NONE` and `UNWIND_USER_TYPE_FP`. `struct unwind_stacktrace` carries output count and entries buffer. `struct unwind_user_frame` describes CFA, return-address, and frame-pointer offsets. `struct unwind_user_state` tracks current IP/SP/FP, selected/current type mask, topmost/done flags, and architecture working state.

Control flow: architecture unwind code advances `unwind_user_state` frame by frame, selecting available methods by priority and writing IPs into `unwind_stacktrace`.

State and persistence: state is temporary for one stack walk. No storage is persistent.

Dependencies and integration points: depends on `linux/types.h` and is shared by generic and architecture-specific unwind implementations.

Risks and test signals: risks include wrong signed offsets, failing to mark done, type priority drift as new methods are added, and stacktrace buffer overruns. Test frame-pointer walks, malformed frames, empty/maxed output buffers, and mixed architecture implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_user_types.h -->
