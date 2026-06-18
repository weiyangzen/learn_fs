# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-test.c

Purpose: provides a debugfs-based generic mailbox exerciser. It lets developers send short signals/messages through named TX/RX mailbox channels, optionally copy payloads through MMIO windows, and read received data as hexdumps from userspace.

Important APIs/types/functions: `struct mbox_test_device` stores channels, MMIO mappings, buffers, locks, wait queue, async notification, and debugfs root. File operations cover `signal` writes, `message` read/write/poll/fasync, and client callbacks `mbox_test_receive_message`, `mbox_test_prepare_message`, and `mbox_test_message_sent`.

Control flow: probe maps optional TX/RX MMIO resources, requests `tx` and `rx` channels by name, creates debugfs files, and allocates an RX buffer when RX exists. Writing `message` copies userspace data, optionally writes the payload to TX MMIO in `tx_prepare`, and sends either the signal or message through `mbox_send_message`. RX callback copies from RX MMIO or the callback payload, marks `data_ready`, wakes readers, and sends SIGIO. Reads block unless data is ready or `O_NONBLOCK` is set, then emit a fixed-size hexdump and clear the buffer.

State and persistence: runtime state is in-memory only: message/signal scratch buffers, `rx_buffer`, `data_ready`, and async queue. Debugfs entries persist while the platform device is bound.

Dependencies and integration: depends on debugfs, mailbox client API, optional MMIO resources, wait queues, fasync, and DT compatible `mailbox-test`.

Risks: the test client assumes up to 128-byte payloads and can expose hardware-specific mailbox behavior through debugfs. Blocking sends use `tx_block` with a 500 ms timeout; controllers without reliable txdone can make writes fail or hang until timeout.

Test signals: manual debugfs send/read, poll and SIGIO behavior, no-RX/no-TX cases, MMIO and non-MMIO modes, and probe-defer when no channels are available.
