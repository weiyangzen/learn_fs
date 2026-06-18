# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-debug.h

Purpose: provides inline string decoders for CDNSP TRBs, completion codes, ring types, slot contexts, endpoint contexts, and PORTSC values. The complete 584-line file was read. It turns raw xHCI-like device-controller bitfields into trace/debug text.

Important APIs/types/functions: `cdnsp_trb_comp_code_string()`, `cdnsp_trb_type_string()`, `cdnsp_ring_type_string()`, `cdnsp_slot_state_string()`, `cdnsp_decode_trb()`, `cdnsp_decode_slot_context()`, `cdnsp_portsc_link_state_string()`, `cdnsp_decode_portsc()`, `cdnsp_ep_state_string()`, `cdnsp_ep_type_string()`, and `cdnsp_decode_ep_context()`.

Control flow: synchronous formatting only. `cdnsp_decode_trb()` switches across link, transfer, completion, port, setup, data, status, normal/isoc/no-op, slot/address/config/evaluate/reset/stop/set-dequeue, endpoint NRDY, and unknown TRBs. Context decoders unpack bitfields into readable summaries.

State and persistence: no hardware ownership. Most helpers write into caller buffers; `cdnsp_decode_slot_context()` uses a static 1024-byte buffer and is not reentrant.

Dependencies/integration: relies on macros/types from `cdnsp-gadget.h`; used by CDNSP tracepoints and debug prints.

Risks: static string buffer can be overwritten by concurrent/nested callers; unknown hardware codes need decoder maintenance; malformed endpoint IDs can produce confusing endpoint names; long formatted output may truncate.

Test signals: compile trace users, feed representative raw TRBs into decoders, and compare runtime traces during enumeration, transfer, stall/reset, suspend/resume, and port changes.
