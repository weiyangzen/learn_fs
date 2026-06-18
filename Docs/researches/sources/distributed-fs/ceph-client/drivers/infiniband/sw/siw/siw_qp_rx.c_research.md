# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp_rx.c

Purpose: Implements the receive-side TCP-to-iWARP parser and executor. It consumes stream bytes from TCP skbs, reconstructs MPA FPDUs, validates DDP/RDMAP headers, places SEND/WRITE/READ RESPONSE payloads into registered memory, creates READ RESPONSE work for inbound READ REQUESTs, validates CRC/trailers, completes received messages, and drops the connection on protocol errors.

Important APIs/types/functions: Data movers include `siw_rx_umem()`, `siw_rx_kva()`, `siw_rx_pbl()`, and `siw_rx_data()`. Header validators include `siw_send_check_ntoh()`, `siw_write_check_ntoh()`, and `siw_rresp_check_ntoh()`. Opcode handlers are `siw_proc_send()`, `siw_proc_write()`, `siw_proc_rreq()`, `siw_proc_rresp()`, and `siw_proc_terminate()`. `siw_get_hdr()` parses minimum and full iWARP headers; `siw_get_trailer()` validates padding/CRC. `siw_rdmap_complete()` finalizes complete RDMAP messages. `siw_tcp_rx_data()` is the main TCP read callback routine.

Control flow: `siw_tcp_rx_data()` loops while skb bytes remain and advances `SIW_GET_HDR`, `SIW_GET_DATA_START/MORE`, and `SIW_GET_TRAILER`. Once a full FPDU trailer validates, it completes the RDMAP message if `DDP_FLAG_LAST` is set. SEND consumes RQ/SRQ entries, WRITE resolves remote target STag, RRESP matches ORQ read state, RREQ creates TX-side READ RESPONSE work, and TERM logs peer error then resets.

State and persistence behavior: RX state is held in `siw_rx_stream` and two `siw_rx_fpdu` contexts for tagged and untagged interleaving. It tracks MSN, tagged offsets, current WQE, SGE/PBL indices, CRC accumulator, partial-header/data/trailer progress, and suspend status. No persistent storage.

Dependencies/integration: Uses skb copy APIs, page mapping, memory validation helpers, QP/CQ completion helpers, SRQ events, TX scheduling for read responses, and CM drop scheduling.

Risks: TCP fragmentation means every state transition must tolerate partial headers, payloads, and trailers. Protocol errors must set correct TERM info and complete/flush local WQEs safely. CRC over userspace buffers deliberately uses skb data to avoid races. RRESP matching to ORQ is security-critical.

Test signals: Fragment every FPDU boundary, CRC success/failure, padding lengths 0-3, SEND with too-small RQ, SRQ limit event, WRITE invalid STag/key/bounds/permission, RRESP without ORQ, READ REQUEST IRQ exhaustion, interleaved tagged/untagged messages, remote TERM parsing, and close during partial receive.
