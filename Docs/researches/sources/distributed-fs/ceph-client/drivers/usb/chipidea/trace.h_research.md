# sources/distributed-fs/ceph-client/drivers/usb/chipidea/trace.h

Purpose: defines ChipIdea gadget-mode tracepoints for formatted controller logs and transfer descriptor preparation/completion.

Important APIs/types/functions: declares `TRACE_SYSTEM chipidea`, `CHIPIDEA_MSG_MAX`, `ci_log`, `TRACE_EVENT(ci_log)`, event class `ci_log_trb`, and concrete events `ci_prepare_td` and `ci_complete_td`.

Control flow: no direct runtime flow; tracepoint macros generate logging hooks. `ci_log_trb` snapshots endpoint name, request pointer, TD pointer/DMA, remaining size, next pointer, token, and endpoint type, then formats transfer size/status fields.

State and persistence: trace events persist in ftrace buffers only. They expose live request/TD metadata but do not mutate controller state.

Dependencies and integration: includes ChipIdea core and UDC headers because it references `struct ci_hw_ep`, `struct ci_hw_req`, `struct td_node`, TD token masks, and endpoint descriptors. The trailing `define_trace.h` block requires Makefile include-path support.

Risks: trace callers must pass valid endpoint/request/TD pointers. TD token decoding depends on UDC data-structure layout and masks staying consistent.

Test signals: build with `CONFIG_USB_CHIPIDEA_UDC`, enable `chipidea:ci_prepare_td` and `chipidea:ci_complete_td`, then run gadget transfer tests to verify TD lifecycle traces.
