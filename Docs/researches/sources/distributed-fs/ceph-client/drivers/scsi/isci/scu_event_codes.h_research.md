# sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_event_codes.h

Purpose: defines SCU event-code construction, masks, event type/specifier constants, and decoding macros for non-task hardware events, especially remote-node events consumed by the RNC state machine.

Important APIs/macros: event type occupies bits 24-27 and event specifier bits 18-23. `SCU_EVENT_TYPE()`, `SCU_EVENT_SPECIFIC()`, and `SCU_EVENT_MESSAGE()` construct event codes. `scu_get_event_type()`, `scu_get_event_specifier()`, and `scu_get_event_code()` decode incoming event dwords. Event families include SMU command/PCQ/register/PCIe/reset errors, transport ACK/NAK timeout, broadcast changes, OSSP link/phy/rate events, fatal internal memory errors, RNC TX/TX_RX suspend, RNC misc operations, error-count events, PTX schedule events, task timeout, and I_T nexus timeout.

Control flow: `remote_node_context.c` uses combined event codes to recognize post complete, invalidate complete, and RNC release events; it uses event types to accept suspend notifications during invalidate/resume and to transition ready/awaiting RNCs to suspended states. Request completion handling uses `SCU_EVENT_TL_RNC_SUSPEND_TX` and `SCU_EVENT_TL_RNC_SUSPEND_TX_RX` as suspend-type arguments when a completion implies upcoming hardware suspension.

State and persistence behavior: no state is stored here. The constants define hardware event ABI values. The event code is a transient dword received from the controller and routed to state machines.

Dependencies/integration: relies on `u32` from includers. It pairs with context commands in `scu_task_context.h`, because post/invalidate/resume commands produce corresponding events. It also supports broader controller/port/link event dispatch outside this subset.

Risks: typo-compatible naming matters: `SCU_EVENT_POST_RCN_RELEASE` omits the second "N" and must match current users. Confusing type-only versus full-code comparisons can accept the wrong event. Test signals include RNC post/invalidate/resume event transitions, driver-posted suspend event decoding, broadcast/link event routing, and masking of unrelated low bits in hardware event dwords.
