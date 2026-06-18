## sources/distributed-fs/beegfs/meta/source/pmq/pmq_logging.hpp

Purpose: declares PMQ log options, formatting entry points, convenience macros, and the small low-level `Log_Message` transport used by test builds.

Important APIs and types: log flags encode errno inclusion and severity in `PMQ_Msg_Options`. `PMQ_Source_Loc` captures file and line. Macros such as `pmq_msg_f`, `pmq_warn_f`, `pmq_perr_ef`, and `pmq_debug_ef` build options with source location. `Log_Message` is a fixed 256-byte record minus the `size_t` field.

Control flow: PMQ code calls macros rather than constructing options manually. All macros funnel into `pmq_msg_of`, which uses `pmq_msg_ofv` from the `.cpp` implementation.

State and persistence behavior: no persistent state. The source-location data is included in options and may be used by the BeeGFS logger.

Dependencies and integration points: includes `pmq_base.hpp` for the printf-format attribute. The low-level reader/writer declarations match the test-mode global log buffer.

Risks: `PMQ_MSG_OPTIONS((lvl), 0)` relies on aggregate initialization and variadic macro behavior that is compiler-sensitive. The 256-byte low-level message limit means high-detail PMQ errors can be truncated.

Test signals: compile-time format checking, macro expansion tests, and log truncation tests are the highest-value coverage.
