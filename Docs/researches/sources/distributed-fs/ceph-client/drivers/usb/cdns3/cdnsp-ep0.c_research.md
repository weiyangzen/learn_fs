# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ep0.c

Purpose: implements CDNSP endpoint-zero setup request handling. The complete 483-line file was read. It handles USB standard requests that affect controller state and delegates other setup packets to the bound gadget driver.

Important APIs/types/functions: exported `cdnsp_status_stage()` and `cdnsp_setup_analyze()`; internal `cdnsp_ep0_stall()`, `cdnsp_ep0_delegate_req()`, `cdnsp_ep0_set_config()`, `cdnsp_ep0_set_address()`, `cdnsp_ep0_handle_status()`, `cdnsp_enter_test_mode()`, feature handlers for device/interface/endpoint recipients, `cdnsp_ep0_set_sel()`, `cdnsp_ep0_set_isoch_delay()`, and `cdnsp_ep0_std_request()`.

Control flow: setup events call `cdnsp_setup_analyze()`, which validates state, repairs halted EP0 software state, dequeues any previous pending EP0 request, detects data/status stage shape, handles standard requests locally or calls `gadget_driver->setup()` with the spinlock dropped, then queues status, stalls, or honors delayed status.

State and persistence: mutates `setup`, `ep0_stage`, `three_stage_setup`, `ep0_expect_in`, `device_address`, `may_wakeup`, U1/U2 flags, test mode, gadget state, isoch delay, and endpoint halt bits. Uses persistent internal `ep0_preq` and `setup_buf`.

Dependencies/integration: Linux USB gadget/composite APIs, Chapter 9 constants, CDNSP queue/halt/reset/setup-device helpers, and tracepoints. Delegates upper-layer policy to the gadget driver's `setup()` callback.

Risks: strict USB state checks are required for SET_ADDRESS/CONFIGURATION/U1/U2/test mode; `wIndex` to endpoint-index conversion must match CDNSP endpoint layout; function remote-wakeup counter can drift if requests are unbalanced; stale EP0 requests must be removed on a new setup packet.

Test signals: enumerate through SET_ADDRESS/SET_CONFIGURATION, GET_STATUS for all recipients, endpoint halt/clear, U1/U2 and remote wakeup features, SET_SEL, SET_ISOCH_DELAY, delayed status, invalid request stalls, and class/vendor delegation.
