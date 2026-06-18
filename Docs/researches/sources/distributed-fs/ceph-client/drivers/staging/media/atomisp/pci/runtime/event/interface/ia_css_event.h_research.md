# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/event/interface/ia_css_event.h

Purpose: declares the software-event pack/unpack helpers used by host/SP event queues.

Important APIs/types: `ia_css_event_encode(u8 *in, u8 nr, uint32_t *out)` packs up to `MAX_NR_OF_PAYLOADS_PER_SW_EVENT` byte payloads into one 32-bit event; `ia_css_event_decode(u32 event, uint8_t *payload)` unpacks a raw event word into a four-byte payload. It depends on `type_support.h` and `sw_event_global.h`.

Control flow and state: the header is stateless and only defines the ABI. Callers allocate payload storage and pass the resulting event words to queue/eventq code.

Integration points: `runtime/event/src/event.c` implements the declarations; `runtime/eventq/src/eventq.c` uses them around `ia_css_queue_enqueue`/`dequeue`; higher layers such as pipeline/bufq send SP software events.

Risks: the API exposes raw pointers and does not express buffer length for `payload`; correctness relies on callers providing at least four bytes and valid `nr`.

Test signals: compile inclusion from both event and eventq paths, encode/decode four-byte round trips, invalid `nr` assertion/return behavior, and event-specific decode cases.
