# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/hardware.c

## Purpose
`hardware.c` is the low-level hardware/protocol engine for the IPWireless 3G PCMCIA driver. It manages card startup, version-specific I/O register access, transmit fragmentation, receive reassembly, setup protocol negotiation, modem-control signaling, interrupt handling, deferred bottom halves, and delivery to the network/tty-facing layer.

## Important APIs, Types, and Functions
The main private type is `struct ipw_hardware`, which owns base I/O addresses, hardware version, MTU, lock, setup timer, TX priority queues, RX queue/pool, packet assemblers, tasklet, work item, network pointer, memory-mapped register pointers, IRQ/removal/shutdown state, and control-line state.

Public functions are `ipwireless_hardware_create()`, `ipwireless_hardware_free()`, `ipwireless_interrupt()`, `ipwireless_set_DTR()`, `ipwireless_set_RTS()`, `ipwireless_send_packet()`, `ipwireless_associate_network()`, `ipwireless_stop_interrupts()`, `ipwireless_init_hardware_v1()`, `ipwireless_init_hardware_v2_v3()`, and `ipwireless_sleep()` as declared in the header. Internal core helpers include `do_send_fragment()`, `do_send_packet()`, `do_receive_packet()`, `queue_received_packet()`, `ipw_receive_data_work()`, `send_pending_packet()`, `ipwireless_do_tasklet()`, and setup handlers.

## Control Flow
Creation initializes queues, locks, tasklet, work item, and setup timer. Version init records I/O or memory-mapped register addresses and card callbacks. V2/V3 startup schedules `ipwireless_setup_timer()`, which periodically marks `to_setup`, resets TX readiness, and schedules the tasklet until version negotiation succeeds or retries are exhausted.

TX callers allocate an `ipw_tx_packet`, enqueue it by priority, and call `flush_packets_to_hw()`. The tasklet sends only setup priority while initialization is pending. `do_send_packet()` fragments logical packets into first/following NL fragments with protocol/address/rank headers, writes fragments through version-specific I/O, and requeues partially sent packets at high priority until complete.

Interrupt handling is version-specific. V1 reads/acks IOIR bits and sets `tx_ready` or increments `rx_ready`. V2/V3 reads memory status registers, detects old/new TX register mode, filters timer-recovery duplicate serials, marks RX/TX readiness, acknowledges PCMCIA interrupts, and schedules the tasklet. RX reads a fragment, swaps bitfields on big-endian systems, dispatches DATA/CTRL/SETUP protocols, assembles DATA by channel, queues completed packets, and uses process-context work to notify the network layer because tty flip paths can sleep.

## State and Persistence Behavior
All state is in `struct ipw_hardware` and runtime queues. `control_lines[]` preserves DTR/RTS/CTS/DCD/DSR/RI bits per channel. `packet_assembler[]` holds partially reassembled DATA packets. `rx_bytes_queued` and `blocking_rx` implement backpressure. `to_setup`, `initializing`, `init_loops`, `last_memtx_serial`, and `serial_number_detected` encode setup and interrupt recovery state. No state is persisted to disk.

## Dependencies and Integration Points
The file depends on Linux IRQ, tasklet, workqueue, timer, I/O accessor, spinlock, list, and allocation APIs. It integrates upward with `network.c` through `ipwireless_network_packet_received()`, `ipwireless_network_notify_control_line_change()`, and `ipwireless_ppp_mru()`. It uses setup protocol definitions from `setup_protocol.h` and device constants from `main.h`.

## Risks and Edge Cases
The driver mixes IRQ, tasklet, workqueue, timer, and process-context teardown, so `shutting_down`, timer deletion, `synchronize_irq()`, tasklet state, and `flush_work()` ordering are important. Several allocations in send paths use `GFP_ATOMIC`. RX backpressure blocks hardware reads once queued data exceeds `IPWIRELESS_RX_QUEUE_SIZE`. Bitfield byte order is manually swapped for big-endian builds. V2/V3 interrupt handling must distinguish real serial-numbered events from duplicate timer recovery interrupts and may switch between `memreg_tx_new` and old TX registers.

## Test Signals
Signals include card startup version query/response, fallback from TX2 to TX register, successful setup config/open/info exchange, DTR/RTS control packets, TX fragmentation across MTU boundaries, RX DATA reassembly, CTRL line-change notifications, queue backpressure/unblock, V1 and V2/V3 interrupt paths, reboot message ACK/callback, and clean shutdown/free with no callbacks after `ipwireless_stop_interrupts()`.
