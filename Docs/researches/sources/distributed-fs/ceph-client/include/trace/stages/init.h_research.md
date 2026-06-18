# sources/distributed-fs/ceph-client/include/trace/stages/init.h

Purpose: Initializes trace event code generation with trace-system string creation and enum/sizeof mapping support.

Important APIs/types/functions: Defines token-pasting helpers `__app__`, `__app`, `TRACE_SYSTEM_STRING`, `TRACE_MAKE_SYSTEM_STR`, `TRACE_DEFINE_ENUM`, and `TRACE_DEFINE_SIZEOF`. It emits `trace_eval_map` records for symbolic enum and sizeof decoding.

Control flow: Early trace generator stages include this file before expanding event headers. `TRACE_DEFINE_ENUM` and `TRACE_DEFINE_SIZEOF` expand into linker-visible map entries used by trace tooling.

State/persistence: It creates static/linker-section metadata, not runtime mutable state.

Dependencies/integration: Included by `trace_events.h` and `trace_custom_events.h`; depends on trace event map definitions.

Risks: Linker-section naming and token pasting are sensitive to `TRACE_SYSTEM_VAR`; mistakes break enum decoding across all trace systems.

Test signals: Build trace headers that call `TRACE_DEFINE_ENUM`/`TRACE_DEFINE_SIZEOF` and inspect generated format/printk maps.
