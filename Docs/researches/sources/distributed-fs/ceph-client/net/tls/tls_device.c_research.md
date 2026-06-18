# sources/distributed-fs/ceph-client/net/tls/tls_device.c

## Purpose
Implements kTLS hardware offload for TX and RX. It attaches TLS contexts to netdevices, builds TX record metadata for NIC encryption, tracks records for retransmission fallback, handles TX/RX resync, falls back when devices go down, and registers netdevice notifiers.

## Important APIs, Types, And Functions
Public functions include `tls_device_sk_destruct`, `tls_device_free_resources_tx`, `tls_offload_tx_resync_request`, `tls_device_sendmsg`, `tls_device_splice_eof`, `tls_get_record`, `tls_device_write_space`, `tls_device_rx_resync_new_rec`, `tls_device_decrypted`, `tls_set_device_offload`, `tls_set_device_offload_rx`, `tls_device_offload_cleanup_rx`, `tls_device_init`, and `tls_device_cleanup`. Global state includes `device_offload_lock`, `destruct_wq`, `tls_device_list`, `tls_device_down_list`, `tls_device_lock`, and `dummy_page`.

## Control Flow And State
TX offload validates the route netdev, hardware features, TLS 1.2, and offloadable cipher, initializes protocol info and fallback AEAD, creates a start-marker record, registers the flow with `tls_dev_add`, attaches the context, and installs `tls_validate_xmit_skb`. Sendmsg serializes on `tx_lock`, copies or splices user data into page fragments, closes records with tag placeholders and headers, pushes scatterlists through TCP, and records sequence ranges for retransmission. ACK cleanup deletes fully acknowledged records. RX offload allocates RX context, enables software RX parsing, adds the device flow, and uses resync modes for driver-requested, core-next-hint, and async request handling. Device-down handling blocks new offloads, moves contexts out of the active list, disables xmit offload, clears netdev pointers, sets degraded RX, synchronizes network readers, deletes driver contexts, and leaves final memory cleanup to socket destruction or refcount completion.

## Dependencies And Integration Points
Integrates with netdevice `tlsdev_ops`, TCP write sequencing and clean-acked callbacks, TLS software parser/decrypt fallback, xmit validation hooks, socket destructors, page fragments, scatterlists, RCU, refcounts, workqueues, and TLS tracepoints.

## Risks And Test Signals
Risk is high around context lifetime, device-down races, refcount/list transitions, partial records, retransmission of records already acked, RX mixed decrypted/ciphertext skbs, resync request wraparound, and fallback after route/device changes. Test signals include TX/RX offload setup failures, NIC down while traffic is active, retransmission over a non-offload device, splice/sendfile with zerocopy, partial writes and MSG_MORE/EOR validation, RX resync modes, socket close during notifier handling, and trace/stat increments.
