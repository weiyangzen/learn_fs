# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_ipmb.c

Purpose: IPMI system-management-interface driver that sends host IPMI traffic over IPMB/I2C to a remote management controller and handles IPMB direct messages.

Important APIs, types, and functions: `struct ipmi_ipmb_dev`, `valid_ipmb()`, `ipmi_ipmb_check_msg_done()`, I2C slave callback, transmit formatting, kernel transmit thread, SMI handlers, cleanup/remove, and probe.

Control flow: probe reads BMC/retry properties, optionally creates a separate slave I2C client, registers slave callback, starts a transmit kthread, and registers an IPMI SMI. The slave callback accumulates inbound bytes and validates complete messages on STOP/read. Commands are forwarded to IPMI core; matching responses complete `working_msg` and signal `got_rsp`. The transmit thread waits for queued messages, formats IPMB checksums/addresses/sequence, sends via `i2c_transfer()`, retries command timeouts, and fabricates IPMI completion responses on bus errors/timeouts or for transmitted responses.

State and persistence: per-device SMI pointer, I2C clients, ready flag, current sequence, retry settings, next/working messages, kthread semaphores, buffers, receive overrun flag, and spinlock.

Dependencies and integration: I2C master/slave, IPMI SMI core, OF properties, kthreads, semaphores, spinlocks, IPMI completion codes, and `ipmb_checksum()`.

Risks and test signals: `BUG_ON(next_msg)` assumes upper layer serialization; remove/cleanup order must stop the thread and unregister slave safely. Tests should cover checksum validation, command vs response paths, sequence matching, retries/timeouts, bus errors, overrun, separate slave adapter, stop during pending message, and SMI registration failure unwind.
