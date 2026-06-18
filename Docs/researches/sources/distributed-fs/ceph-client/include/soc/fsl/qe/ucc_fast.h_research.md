# sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc_fast.h

Purpose: declares Fast UCC status bits, configuration enums, private state, and lifecycle/control APIs for high-speed QE protocol channels.

Important APIs and types: macros define 32-bit and 16-bit RX/TX buffer descriptor ownership, wrap, interrupt, first/last, continuous, and error bits. Alignment and FIFO sizing constants constrain buffers and virtual FIFO registers. Enums configure protocol mode, transparent TX/RX, diagnostic mode, sync length, RTS behavior, NRZ/NRZI encoding, and CRC length. `struct ucc_fast_info` carries UCC/TDM number, clocks/syncs, registers, IRQ, mask, mux flags, FIFO sizes, max RX length, protocol mode, encoding, CRC, and sync length. `struct ucc_fast_private` tracks mapped registers/event/mask pointers, enabled/stopped state, FIFO MURAM offsets, optional stats, and MRBLR. APIs initialize/free, enable/disable directions, handle IRQs, transmit-on-demand, compute command subblocks, and dump registers.

Control flow: callers fill `ucc_fast_info`, initialize resources and FIFOs, enable RX/TX, handle interrupts, optionally force TX polling, then disable/free on teardown.

State and persistence: runtime state includes hardware registers, MURAM FIFO allocations, enabled/stopped flags, event masks, and optional counters. No persistent data.

Dependencies and integration points: includes QE, immap, and common UCC headers; used by fast protocols such as Ethernet, HDLC/POS/ATM, and TDM users.

Risks and test signals: risks include FIFO alignment/size mistakes, BD status width confusion, stale enabled/stopped flags, command subblock mismatch, and IRQ mask loss. Test initialization failure unwinding, TX/RX enable/disable, IRQ paths, transmit-on-demand, each protocol mode used by drivers, and MURAM leak checks.
