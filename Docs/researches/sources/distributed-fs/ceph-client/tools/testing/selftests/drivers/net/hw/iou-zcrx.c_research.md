# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/iou-zcrx.c

Purpose: C client/server helper for testing io_uring zero-copy receive (`IORING_OP_RECV_ZC`) with network interface queue registration.

Important APIs/types/functions: `liburing`, custom `t_io_uring_zcrx_ifq_reg`, `io_uring_register_ifq`, `io_uring_zcrx_area_reg`, `io_uring_region_desc`, `io_uring_zcrx_rq`, `parse_address()`, `get_refill_ring_size()`, `setup_zcrx()`, `add_accept()`, `add_recvzc()`, `add_recvzc_oneshot()`, `process_accept()`, `process_recvzc()`, `server_loop()`, `run_server()`, `run_client()`, `parse_opts()`, and `main()`.

Control flow: `main()` allocates a deterministic payload, parses server/client options, and runs either a TCP server or client. The server opens an IPv6 socket, initializes an io_uring with CQE32 and task-run flags, registers an interface queue and user refill ring/memory area, accepts one connection, posts multishot or one-shot zero-copy receives, validates payload bytes from CQEs against the known pattern, and returns buffers to the refill ring. The client connects and sends the payload in configured chunks.

State and persistence: Uses global config and runtime counters, mmaps receive area and refill ring, owns one TCP connection, and writes refill-ring tail. No persistent files.

Dependencies and integration points: Requires new liburing/kernel ZCRX APIs, io_uring, NIC queue support, optional huge pages for large chunks, and the Python `iou-zcrx.py` orchestrator.

Risks and test signals: Skips with code 42 for unsupported large chunks/huge pages. Failures indicate registration, refill-ring, CQE parsing, payload integrity, oneshot/multishot, or queue binding regressions.
