# sources/distributed-fs/ceph-client/drivers/nfc/pn533/usb.c

Purpose: Implements PN533 USB transport, including native PN533 devices, Sony PaSoRi, and ACS ACR122U CCID-wrapped devices.

Important APIs and functions: `struct pn533_usb_phy` stores USB device/interface, IN/OUT/ACK URBs, ACK buffer, and common PN533 pointer. Native flow uses `pn533_usb_send_frame()`, `pn533_recv_ack()`, `pn533_recv_response()`, `pn533_usb_send_ack()`, and `pn533_usb_abort_cmd()`. ACR122 support defines CCID/APDU frame structs and `pn533_acr122_frame_ops`, plus `pn533_acr122_poweron_rdr()`.

Control flow: Probe allocates URBs/buffer, finds bulk endpoints, initializes URBs, selects protocols/frame ops based on USB id, powers on ACR122 readers when needed, initializes common PN533, finalizes setup, and registers NFC. Sending submits the OUT URB synchronously via completion, then submits IN URB for ACK or direct response based on protocol type. ACK completion validates ACK before requesting the response. Response completion wraps actual bytes in an SKB and calls `pn533_recv_frame()`.

State and persistence: Runtime state is URB ownership, ACK buffer, common PN533 command state, and device variant. No durable persistence.

Dependencies and integration points: Uses Linux USB core, PN533 common core, NFC registration, and alternate frame ops for ACR122 CCID escape framing.

Risks: ACR122 cannot safely abort commands, so stop-poll semantics differ. URB context is temporarily swapped for synchronous OUT/power-on completions. IN buffer sizing assumes max standard/extended frame length. Test signals include each USB id variant, native ACK/response path, req/resp-only ACR122 path, invalid ACK, URB cancellation/disconnect, ACR122 power-on, alternate frame validation, and setup failure cleanup.
