# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ncdevmem.c

Purpose: C netcat-like helper for TCP device-memory tests using udmabuf as a mock dmabuf provider; supports RX devmem, TX devmem, validation, queue binding, header split, RSS steering, and zerocopy completions.

Important APIs/types/functions: `struct memory_buffer`, `struct memory_provider`, `udmabuf_alloc/free`, DMA_BUF sync ioctls, `validate_buffer()`, command helpers, `ethtool_add_flow()`, `rxq_num()`, `reset_flow_steering()`, `get_ring_config()`, `restore_ring_config()`, `configure_headersplit()`, `configure_rss()`, `check_changing_channels()`, `configure_flow_steering()`, `bind_rx_queue()`, `bind_tx_queue()`, `enable_reuseaddr()`, `parse_address()`, `create_queues()`, `do_server()`, `run_devmem_tests()`, `wait_compl()`, `do_client()`, and `main()`.

Control flow: Without server/client addresses, `main()` runs self-tests that allocate udmabuf memory, discover queues, configure RSS and header split, verify invalid bind cases fail, bind RX queues, and ensure channel deactivation is rejected while queues are bound. In server mode, it enables header split/RSS, installs ntuple steering, binds RX queues to a dmabuf through YNL netdev `bind-rx`, listens for TCP, receives with `MSG_SOCK_DEVMEM`, parses `SCM_DEVMEM_DMABUF`/`SCM_DEVMEM_LINEAR` control messages, validates/copies fragments, and returns tokens with `SO_DEVMEM_DONTNEED`. In client mode, it binds TX dmabuf, enables `SO_ZEROCOPY`, copies stdin into udmabuf, sends `SCM_DEVMEM_DMABUF` with `MSG_ZEROCOPY`, and waits for error-queue zerocopy completion.

State and persistence: Creates udmabuf/memfd mappings, mutates ethtool channels/rings/RSS/ntuple rules, binds netdev RX/TX queues to dmabufs, uses sockets and error queues, and cleans most state via explicit unwind labels.

Dependencies and integration points: Requires `/dev/udmabuf`, DMA_BUF sync, YNL-generated `netdev-user.h` and `ethtool-user.h`, netdev devmem APIs, ethtool Netlink, ntuple support, header split, RSS, zerocopy sockets, and queue-capable hardware.

Risks and test signals: Complex cleanup means partial setup failures can leave device config if unwind is wrong. Failures indicate devmem queue binding, header split, RSS steering, dmabuf token, linear fallback, zerocopy TX completion, or validation regressions.
