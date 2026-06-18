# sources/distributed-fs/orangefs/src/common/events/fmt_api.h

Purpose: Declares shared TAU trace-format helper structures and global variables used by the PVFS/TAU event API.

Important APIs/types: Defines thread/event/string limits, `TAU_Log_get_event_number()`, `Ttf_closed_event_def` with start/end `ff_format` parsers and event IDs, and `Ttf_thread_bundle` with event table, TAU file handle, event counters, scratch buffer, and scratch position. Declares `g_t_bundles`, `g_pid`, `g_traceloc`, `g_filepfx`, and `g_defbufsz`.

Control flow contract: Event definitions are parsed into `ff_format` objects, copied into per-thread bundles, and used to encode varargs into fixed scratch storage before writing TAU events.

State/persistence: Exposes global process and per-thread trace state. Each thread bundle owns its event table and TAU output handle.

Dependencies/integration: Includes TAU writer headers and `fmt_fsm.h`; it is C++-style despite `.h` extension, with constructors and assignment operators.

Risks: Duplicates structure definitions also present in `pvfs_tau_api.c`, which can drift. `strncpy()` calls do not always force termination when inputs are long. Scratch buffer size is fixed.

Test signals: Build with `BUILD_TAU`, define events with multiple format strings, and validate per-thread refresh copies all event metadata.
