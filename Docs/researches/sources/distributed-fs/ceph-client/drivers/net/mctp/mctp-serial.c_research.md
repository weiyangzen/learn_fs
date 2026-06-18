<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-serial.c -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-serial.c

Purpose: implements DSP0253 MCTP over serial as the `N_MCTP` TTY line discipline. Opening the line discipline creates an MCTP netdev over the attached tty; closing unregisters it.

Important APIs/types/functions: `struct mctp_serial` holds the tty, netdev, IDA index, spinlock, TX work item, TX/RX state machines, FCS values, lengths, positions, and fixed buffers. Key functions are `next_chunk_len`, `mctp_serial_tx_work`, `mctp_serial_tx`, `mctp_serial_tty_receive_buf`, `mctp_serial_push_header`, `mctp_serial_push`, `mctp_serial_rx`, `mctp_serial_open`, and `mctp_serial_close`.

Control flow: TX copies the skb into a bounded buffer, stops the netdev queue, and schedules work. The worker writes the frame delimiter, version, length, escaped payload bytes, FCS, and trailing delimiter, handling partial tty writes and write wakeups. RX consumes bytes from `receive_buf`, runs a framing/escape state machine, validates version and CRC-CCITT FCS, and injects a packet with no link-layer address.

State and persistence: state is per-tty and runtime-only. The IDA allocates stable instance numbers while devices are open. A spinlock protects RX and TX state machines. `TTY_DO_WRITE_WAKEUP` and workqueue scheduling preserve progress across partial writes but no data persists after close.

Dependencies/integration: depends on TTY line discipline registration, CAP_NET_ADMIN for opening, MCTP netdev core, CRC-CCITT helpers, and normal netdevice queueing. It uses a fixed serial MTU of 68 bytes and ARPHRD_MCTP with no hardware header.

Risks and test signals: risks include malformed frames leaving the RX state machine stuck until a delimiter, partial write handling, concurrent tty close versus TX work, and fixed buffer length assumptions. Built-in KUnit coverage exercises `next_chunk_len`; further tests should cover escaping, CRC failure, line discipline permissions, close during TX, and netdev stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-serial.c -->
