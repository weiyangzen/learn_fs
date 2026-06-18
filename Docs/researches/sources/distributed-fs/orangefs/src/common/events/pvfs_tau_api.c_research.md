# sources/distributed-fs/orangefs/src/common/events/pvfs_tau_api.c

Purpose: Implements a C-callable PVFS/OrangeFS tracing API backed by TAU trace files and the local format FSM.

Important APIs/functions: `Ttf_init()` records process/file settings, initializes TAU, creates the master bundle, resets per-thread bundles, and initializes thread 0. `Ttf_thread_start()` registers a TAU thread group, initializes a per-thread trace file, and refreshes event definitions from the master bundle. `Ttf_event_define()` allocates event IDs and start/stop user-event IDs in the master bundle, parses format descriptors, and refreshes the local bundle. `Ttf_EnterState_info_va()` and `Ttf_LeaveState_info_va()` write state enter/leave records and encode event IDs plus formatted varargs into scratch space as `x_uint64` user-event triggers. `Ttf_finalize()` exits dummy states and closes trace files.

Control flow: Global event definitions are serialized by a pthread mutex around the master bundle. Per-thread bundles lazily allocate and are refreshed when an event type is missing or after definitions change. Trace files are named from configured folder, prefix, process id, and TAU thread id.

State/persistence: Persistent output is TAU `.trc` and `.edf` files. In-memory state includes `g_master_bundle`, `g_t_bundles[1024]`, process identifiers, trace path/prefix, default buffer size, and per-thread event counters/scratch buffers.

Dependencies/integration: Requires TAU headers/libraries, pthreads, `fmt_fsm.h`, `pvfs_tau_api.h`, and debug macros. Exposes `extern "C"` symbols for C callers.

Risks: Thread IDs index a fixed 1024-entry array without bounds checks. Memory allocated for bundles/events is not freed in `Ttf_finalize()`. Scratch buffer size is fixed and not checked against encoded payload size. Some API parameters (`process_id`, `thread_id`, start/end times in `Ttf_LogEvent_info`) are ignored or only partly used. Format and event structure definitions duplicate `fmt_api.h`.

Test signals: TAU-enabled integration tests should cover multiple threads, event definition before/after thread start, vararg payload formats, finalization, and oversized format rejection.
