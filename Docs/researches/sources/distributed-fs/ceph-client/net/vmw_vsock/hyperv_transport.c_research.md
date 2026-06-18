# sources/distributed-fs/ceph-client/net/vmw_vsock/hyperv_transport.c

## Purpose
`hyperv_transport.c` implements the Hyper-V guest-to-host AF_VSOCK transport (`hv_sock`). It maps Linux vsock stream sockets to Hyper-V Sockets over VMBus pipe channels, using a fixed service GUID template where the vsock port occupies the first four bytes.

## Important APIs, Types, And Functions
Key state is `struct hvsock`, stored in `vsk->trans`, with service GUIDs, a `struct vmbus_channel`, current receive descriptor, pending payload offsets, and FIN state. Important functions include `hvs_open_connection()`, `hvs_close_connection()`, `hvs_connect()`, `hvs_shutdown()`, `hvs_release()`, `hvs_stream_enqueue()`, `hvs_stream_dequeue()`, `hvs_stream_has_data()`, `hvs_stream_has_space()`, and the `hvs_transport` callback table.

## Control Flow
Module init verifies VMBus protocol support, registers an `hv_driver`, then registers the transport as `VSOCK_TRANSPORT_F_G2H`. On an offered VMBus channel, `hvs_open_connection()` validates the service GUID, locates either a listening socket for host-initiated connects or a `TCP_SYN_SENT` client socket for guest-initiated connects, opens the channel with ring sizes derived from socket buffers, stores the socket as per-channel state, and moves the socket to `TCP_ESTABLISHED`. Host-initiated connections create a child vsock, assign the Hyper-V transport, insert it in the connected table, and enqueue it for accept.

Transmit copies user data into a page-sized `hvs_send_buf` and sends VMBus in-band packets with a small `vmpipe_proto_header`. Receive uses VMBus packet iterators and copies payload directly to the user message. A zero-length packet is FIN and sets peer shutdown. Close sends FIN, waits up to `HVS_CLOSE_TIMEOUT`, then removes the socket if the peer does not complete shutdown.

## State And Persistence
Per-socket state persists in `struct hvsock` and VMBus channel state. The transport does not support datagrams, seqpacket, MSG_PEEK, or local namespace mode. Ring buffer sizing is persistent for the channel lifetime and capped for host compatibility.

## Dependencies And Integration Points
The file depends on Hyper-V VMBus APIs, `hvhdk.h`, socket core callbacks, and the AF_VSOCK transport interface. It integrates with AF_VSOCK through `vsock_core_register()`, socket lookup helpers, connected table insertion, accept queue handling, and stream notification callbacks.

## Risks And Edge Cases
Risks include VMBus channel lifetime versus socket lifetime, host rescind callbacks racing with close, ring-buffer full handling that must reserve space for FIN, malformed packet length validation, and compatibility with older Windows hosts that require small ring buffers. Since `get_local_cid()` returns `VMADDR_CID_ANY`, binding and addressing semantics are narrower than VMCI or virtio.

## Test Signals
Test guest-to-host and host-to-guest connect/listen/accept on Hyper-V, FIN and rescind handling, send buffer pressure, receive of zero-length FIN, invalid service GUID rejection, hibernation suspend/resume dummies, old and new VMBus protocol versions, and module unload with active channels.
