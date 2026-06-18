# sources/distributed-fs/ceph-client/include/net/nfc/llc.h

Purpose: exposes the NFC Link Layer Control manager abstraction that connects HCI framing to a selected lower link implementation such as `nop` or `shdlc`.

Important APIs and types: `LLC_NOP_NAME` and `LLC_SHDLC_NAME` select implementations. Callback types route received skbs to HCI, transmitted skbs to the driver, and failures upward. `struct nfc_llc` is opaque; public functions allocate/free, start/stop, receive from driver, transmit from HCI, and initialize/exit registered LLC providers.

Control flow: HCI allocates an LLC by name, starts it after device open, sends HCI packets through `nfc_llc_xmit_from_hci()`, and lower drivers feed frames into `nfc_llc_rcv_from_drv()`. The LLC invokes callbacks for decoded delivery or failure.

State and persistence: state is implementation-private runtime link state, including queues/windowing for SHDLC. No persistent configuration lives here.

Dependencies and integration points: includes HCI and skbuff headers and sits between NFC HCI core and physical/controller transport drivers.

Risks and test signals: risk is lifecycle mismatch across HCI unregister, link-layer retransmission/failure propagation, and skb ownership errors. Test allocation by name, start/stop idempotence, receive/transmit paths, bad frames, and failure callback teardown.
