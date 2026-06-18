# sources/distributed-fs/ceph-client/drivers/net/can/ti_hecc.c

Purpose: Platform SocketCAN driver for TI HECC hardware, managing registers, mailbox RAM, timestamped RX offload, prioritized TX mailboxes, transceiver regulator, clocking, and suspend/resume.

Important APIs, types, and functions: `struct ti_hecc_priv` contains CAN core, RX offload, MMIO bases, clock, mailbox spinlock, TX head/tail priority counters, and regulator. Key routines include probe/remove, open/close, start/stop/reset, xmit, interrupt, mailbox_read, error/state helpers, and PM callbacks.

Control flow: Probe maps named resources, gets IRQ/clock/regulator, initializes RX offload, and registers. Open requests IRQ, enables transceiver, opens CAN core, starts hardware/offload, and starts queue. TX fills current mailbox, stores echo SKB, decrements priority/head, enables mailbox, and sets transmit request. IRQ handles errors/state changes, TX acknowledgements, RX pending offload, clears flags, and finishes offload.

State and persistence behavior: TX counters encode mailbox index and priority; RX state is hardware mailboxes plus `can_rx_offload`. No persistent settings. Suspend powers down HECC and clock, resume clears powerdown and reattaches queue if running.

Dependencies and integration points: Uses platform/OF APIs, named MMIO resources, clocks, regulators, SocketCAN, timestamp RX offload, echo SKBs, IRQs, and PM.

Risks: `CANME` mailbox enable changes need spinlock protection. RX overflow detection depends on last-mailbox overwrite behavior. TX priority wrap and wake rules are subtle. Bus-off disables interrupts before CAN core handling.

Test signals: TX priority/mailbox wrap, RX timestamp ordering, RX overflow/drop path, bus error/passive/warning/off transitions, regulator failures, `ti,use-hecc1int`, suspend/resume while running, and shared IRQ behavior.
