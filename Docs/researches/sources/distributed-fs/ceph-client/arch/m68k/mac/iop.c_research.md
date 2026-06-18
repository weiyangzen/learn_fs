# sources/distributed-fs/ceph-client/arch/m68k/mac/iop.c

## Purpose
Implements management and message passing for Macintosh I/O Processor chips, 6502-based controllers used for SCC serial and ISM/ADB functions on the IIfx and some Quadras.

## APIs, Flow, And State
Public state is `iop_scc_present` and `iop_ism_present`. Internal state includes `iop_base[NUM_IOPS]`, `iop_msg_pool`, per-IOP/channel send queues, and listener slots. `iop_init()` discovers SCC and ISM IOP base addresses from `macintosh_config`, initializes message pools and listeners, and restarts/clears the ISM alive flag. `iop_register_interrupts()` requests the appropriate ISM interrupt. `iop_listen()` registers channel callbacks. `iop_send_message()` allocates a message, queues it, and starts transmission when idle. Interrupt handling reads IOP INT0/INT1 status bits, drains completed send buffers via `iop_handle_send()`, dispatches unsolicited receive messages via `iop_handle_recv()`, and requires listeners to call `iop_complete_message()`.

## Dependencies And Integration
Depends on `asm/mac_iop.h` shared-memory offsets/states, Mac model data, Mac IRQ numbers, and interrupt APIs. ADB and serial subsystems consume the listener and send-message interface. The code integrates with OSS/VIA interrupt mappings through the chosen IRQ line.

## Risks And Test Signals
The pool allocator returns `NULL` on exhaustion, but `iop_handle_recv()` assumes success. Message state machine errors can stall a channel because each channel has a depth of one. Callbacks run in interrupt context and must be brief or defer work. Test signals are ISM alive checks, ADB keyboard/mouse traffic on IOP machines, SCC compatible mode behavior, and absence of stuck `MSG_NEW`/`MSG_COMPLETE` channel states.
