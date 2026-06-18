# sources/distributed-fs/ceph-client/drivers/char/ipmi/bt-bmc.c

Purpose: Aspeed BMC-side BT host interface exposed as `/dev/ipmi-bt-host` misc device for userspace IPMI handling.

Important APIs, types, and functions: `struct bt_bmc`, register helpers, file operations `bt_bmc_open/read/write/ioctl/release/poll`, IRQ handler, poll timer, `bt_bmc_probe()`, and `bt_bmc_remove()`.

Control flow: probe maps registers, registers misc device, configures IRQ or fallback polling timer, programs BT control registers, and clears BMC busy. Open is single-user via global atomic. Read waits for host-to-BMC attention, sets BMC busy, clears attention/read pointer, reads a length-prefixed message, copies it to userspace, and clears busy. Write waits until host not busy and no B2H attention, writes a response buffer, and sets B2H attention. IRQ or timer wakes waiters.

State and persistence: per-device MMIO base, IRQ/timer, wait queue, mutex, miscdev; global `open_count` serializes all instances. Hardware busy/attention bits hold transient protocol state.

Dependencies and integration: platform/OF for Aspeed compatibles, miscdevice, poll/wait queues, timers, IRQs, MMIO, and `linux/bt-bmc.h` ioctl.

Risks and test signals: global open count prevents multi-instance use; timer setup only occurs when IRQ config fails. Tests should cover IRQ and polling modes, read/write bounds, userspace copy faults, open exclusivity, busy bit transitions, ioctl SMS_ATN, and remove with active timer.
