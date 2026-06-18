<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_sw.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_sw.c

## Purpose
`tls_sw.c` implements the software kTLS record datapath. On TX it builds TLS records from user data, optional splice pages, and BPF verdicts, encrypts with the kernel crypto API, and pushes encrypted scatterlists into TCP. On RX it waits for complete TLS records from `tls_strp.c`, decrypts in place or into user buffers/skbs, handles TLS 1.3 padding and key updates, integrates with sockmap/BPF stream parsing, and exposes recvmsg/splice/read_sock operations.

## Important APIs, Types, and Functions
- `tls_err_abort()` records fatal TLS errors on the socket and wakes waiters.
- TX helpers include `tls_get_rec()`, `tls_free_rec()`, `tls_tx_records()`, `tls_do_encryption()`, `tls_push_record()`, `bpf_exec_tx_verdict()`, `tls_sw_sendmsg_locked()`, `tls_sw_sendmsg()`, `tls_sw_splice_eof()`, `tx_work_handler()`, and `tls_sw_write_space()`.
- RX helpers include `tls_decrypt_sg()`, `tls_decrypt_sw()`, `tls_decrypt_device()`, `tls_rx_one_record()`, `tls_sw_recvmsg()`, `tls_sw_splice_read()`, `tls_sw_read_sock()`, and `tls_sw_sock_is_readable()`.
- Parser callbacks `tls_rx_msg_size()`, `tls_rx_msg_ready()`, and `tls_data_ready()` connect the strparser to the software RX path.
- Resource functions `tls_sw_cancel_work_tx()`, `tls_sw_release_resources_tx()`, `tls_sw_release_resources_rx()`, `tls_sw_strparser_done()`, `tls_sw_free_resources_rx()`, and context free helpers unwind crypto, skbs, work, and parser state.
- `init_prot_info()` and `tls_set_sw_offload()` initialize cipher parameters, AEAD transforms, IV/sequence state, async capability, and TLS 1.3 rekey updates.

## Control Flow
TX starts in `tls_sw_sendmsg()`, which serializes on `ctx->tx_lock` and the socket lock. It processes cmsgs, obtains or allocates an open record, calculates room based on `tx_max_payload_len`, allocates encrypted/plaintext `sk_msg` storage, then copies or zero-copies user pages. At record boundary or end-of-record, `bpf_exec_tx_verdict()` may pass, drop, or redirect plaintext. Passed records are prepared with TLS header/AAD/content type, encrypted asynchronously or synchronously, queued on `tx_list`, and transmitted in order by `tls_tx_records()` or delayed TX work. Partial TCP sends leave `tls_context->partially_sent_record` for later resume.

RX starts in `tls_sw_recvmsg()` or splice/read_sock variants. A single-reader lock prevents queue reordering. Pending decrypted `rx_list` records are drained first. Otherwise `tls_rx_rec_wait()` waits for a complete strparser record or sockmap data, `tls_rx_one_record()` selects device decrypt or software decrypt, sequence numbers advance, and records are copied, zero-copied, queued for async completion, or handed to sockmap/BPF. TLS 1.3 padding is trimmed and non-data record types are reported to userspace through `TLS_GET_RECORD_TYPE` cmsgs. KeyUpdate handshake records set `key_update_pending`, causing future reads to return `-EKEYEXPIRED` until userspace rekeys RX.

## State and Persistence
TX state includes open record, pending encrypted records, async crypto wait state, `encrypt_pending`, delayed work bits, AEAD send transform, and crypto sequence/IV state in `tls_context->tx`. RX state includes the strparser, `rx_list` for decrypted but undelivered records, `async_hold` references, `decrypt_pending`, AEAD receive transform, zero-copy and async capability flags, single-reader flags, and `key_update_pending`. All state is in-memory per socket. Crypto request memory and skb/page references must be released on completion, close, or error.

## Dependencies and Integration Points
The file depends on kernel crypto AEAD APIs, `sk_msg` helpers, TCP send/receive helpers, sockmap/BPF message verdict and stream parser integration, `tls_strp.c`, optional device TLS hooks, poll/read/splice socket operation hooks installed by `tls_main.c`, and MIB counters. It also uses tracepoints from generic sock tracing and reports TLS statistics through `TLS_INC_STATS`.

## Risks and Edge Cases
Major risks are async crypto ordering, page/sk_msg accounting, TLS 1.3 padding and content-type semantics, BPF verdict side effects, and close-time cleanup. Encryption completion may occur out of order, so transmission is allowed only when the list head is ready. Zero-copy decrypt is disabled for TLS 1.3 unless no-padding is expected or the tail confirms data content. BPF `bpf_msg_pop_data()` changes plaintext length and requires encrypted length trimming. Fatal crypto errors set `sk_err` and abort the connection. Reader locking prevents concurrent recvmsg/splice/read_sock from corrupting RX queues.

## Test Signals
Run kTLS selftests across TLS 1.2 and TLS 1.3, all supported ciphers, sync and async crypto drivers, sendmsg/splice/sendpage, cmsg record types, sockmap pass/drop/redirect, `MSG_PEEK`, `MSG_WAITALL`, partial reads, zero-copy RX, device-decrypted fallback, bad padding, bad tags, KeyUpdate and rekey completion, and close with pending async work. KASAN/KCSAN/refcount checks are particularly valuable around `sk_msg`, skb lists, and async request lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_sw.c -->
