# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_common.c

## Purpose
`wx_vf_common.c` provides shared netdev/PCI lifecycle for Wangxun VF drivers. It handles suspend/resume/remove, MSI-X request, API negotiation, reset, receive-mode programming, TX/RX configuration, MAC address changes, link watchdog, open/close, and VF service work.

## Important APIs, Types, and Functions
Exports are `wxvf_suspend()`, `wxvf_shutdown()`, `wxvf_resume()`, `wxvf_remove()`, `wx_request_msix_irqs_vf()`, `wx_negotiate_api_vf()`, `wx_reset_vf()`, `wx_set_rx_mode_vf()`, `wx_configure_vf()`, `wx_set_mac_vf()`, `wxvf_watchdog_update_link()`, `wxvf_open()`, `wxvf_close()`, and `wxvf_init_service()`. Internal flow is split across `wx_configure_rx_vf()`, `wxvf_up_complete()`, `wxvf_down()`, `wxvf_reinit_locked()`, `wxvf_reset_subtask()`, `wxvf_link_config_subtask()`, and `wxvf_service_task()`.

## Control Flow
VF probe code initializes service work here, then open allocates resources, programs RX mode/TX/RX rings, requests MSI-X IRQs, sets real queue counts, enables NAPI/interrupts, starts queues, and schedules service. Link updates are driven by misc interrupts setting `WX_FLAG_NEED_UPDATE_LINK`; service work queries PF/hardware link and toggles carrier. Reset errors set `WX_FLAG_NEED_DO_RESET`, causing the service task to reinitialize under RTNL and `reset_lock`. Close stops service, queues, NAPI, resets the VF, frees IRQs/resources, and cleans rings.

## State and Persistence Behavior
State lives in `struct wx`: service timer/work, flags, reset state bitmap, MSI-X entries, queue vectors, rings, mailbox lock, link/speed, MAC addresses, and allocated resources. Suspend/resume detach or attach the netdev and tear down/recreate interrupt scheme without storing anything persistently.

## Dependencies and Integration Points
The file depends on low-level VF commands from `wx_vf.c`, queue programming from `wx_vf_lib.c`, common ring/resource helpers from `wx_lib.h`, mailbox locking, Linux PCI PM, netdevice carrier and queue APIs, NAPI, timers, workqueues, and IRQ APIs. Concrete VF drivers reuse these functions in netdev ops and PCI PM hooks.

## Risks and Edge Cases
`wx_request_msix_irqs_vf()` calls `wx_reset_interrupt_capability()` on queue IRQ request failure, which may surprise caller cleanup paths. Reset reinit ignores failures from `wx_request_msix_irqs_vf()` during service reset. Receive mode always attempts xcast, multicast, and UC mailbox updates; mailbox failure is not propagated from `ndo_set_rx_mode`. Close and reset both call `wx_reset_vf()`, so PF availability affects teardown latency.

## Test Signals
Open/close repeatedly, suspend/resume with netdev up and down, inject MSI-X request failures, force PF mailbox reset/loss, and verify carrier messages for link transitions. Test MAC change ack/nack, receive mode transitions for promisc/allmulti/multicast, and service reset after PF ping loss.
