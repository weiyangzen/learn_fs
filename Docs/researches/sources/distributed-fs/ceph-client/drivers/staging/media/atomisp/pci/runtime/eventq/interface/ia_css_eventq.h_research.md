# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/eventq/interface/ia_css_eventq.h

Purpose: public interface for sending host-to-SP software events and receiving SP-to-host event payloads through the generic CSS queue abstraction.

Important APIs: `ia_css_eventq_recv(ia_css_queue_t *eventq_handle, uint8_t *payload)` dequeues and decodes an event. `ia_css_eventq_send(ia_css_queue_t *eventq_handle, u8 evt_id, u8 evt_payload_0, u8 evt_payload_1, uint8_t evt_payload_2)` packs and enqueues an event, blocking until the queue is not full.

Control flow/state: the header is stateless; the queue handle carries all local/remote queue state.

Dependencies/integration: depends on `ia_css_queue.h`, with implementation in `eventq.c` and event packing from `ia_css_event.h`.

Risks: the send contract says blocking; users must avoid calling it from atomic contexts if the implementation busy-waits. Payload storage length is not encoded in the receive signature.

Test signals: local and remote queue send/receive, full queue retry behavior, empty receive returning `-ENODATA`, and invalid handle returning `-EINVAL` through queue APIs.
