# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/pio.c

## Purpose

`pio.c` implements the HCI Programmed I/O backend. It drives command, response, data, and IBI FIFOs through MMIO ports, manages linked software queues of `hci_xfer` objects, services FIFO threshold interrupts, handles PIO error recovery, and provides generic IBI pool integration.

## Important APIs, Types, and Functions

- PIO register macros define command/response/data/IBI ports, queue/data thresholds, queue sizes, PIO interrupt status/enable registers, and FIFO level fields.
- `struct hci_pio_data` stores current and tail pointers for command, RX, TX, and response queues, IBI assembly state, threshold sizes, cached threshold register, and enabled IRQ mask.
- `__hci_pio_init()` configures FIFO thresholds, enables status bits, disables signals, and initializes error IRQ tracking.
- `hci_pio_queue_xfer()` links transfer arrays, initializes data counters, queues them under `hci->lock`, starts command processing, and enables needed IRQs.
- `hci_pio_process_cmd()`, `hci_pio_process_tx()`, `hci_pio_process_rx()`, and `hci_pio_process_resp()` move descriptors/data/responses between software queues and FIFOs.
- `hci_pio_err()` completes or discards pending transfers, resets PIO FIFOs, and resumes the HCI controller after errors.
- IBI helpers assemble segmented payloads from `PIO_IBI_PORT` and queue generic IBI slots.

## Control Flow

Initialization derives RX/TX thresholds from hardware queue sizes, writes threshold registers, and records the maximum IBI threshold. Queueing links xfers through `next_xfer`, sets `data_left`, and if no command is active starts processing immediately. Command processing first queues data buffers so TX data or RX space is ready, queues expected responses for `ROC` descriptors, writes descriptor words to the command queue, and advances to the next xfer.

RX/TX processing drains or fills FIFO words while threshold status permits. Response processing reads response descriptors, checks TID against the expected xfer, stores response, handles trailing or over-read RX data, advances data/response queues, and completes waiters. The IRQ handler filters enabled statuses, services IBI/RX/TX/response/error/command-ready events, acknowledges warnings and errors, updates the signal-enable register, and returns whether it handled work.

## State and Persistence Behavior

PIO queue state persists in `hci->io_data` for backend lifetime. Individual xfers remain caller-owned but are referenced by linked lists until completion or dequeue. IBI slot/payload assembly persists across interrupts until the last segment is queued or dropped. Suspend disables PIO signals and marks IRQ inactive; resume reinitializes thresholds.

## Dependencies and Integration Points

PIO uses command descriptor definitions, response decoding, IBI status bits, generic IBI pools, the HCI core spinlock, and core reset/resume helpers. It supports both v1 two-word and v2 four-word descriptors by checking `hci->cmd`.

## Risks and Edge Cases

The backend performs complex recovery for short reads, over-read data pushed into following RX xfers, partial trailing bytes, and timeout dequeue. `hci_pio_do_tx()` may read a full word from memory for trailing bytes beyond the exact buffer length, relying on harmless over-read. Error recovery is intentionally coarse and resets PIO queues. IBI handling must drain payloads even when no slot is available or an error occurred.

## Test Signals

Exercise immediate and buffered transfers, multi-xfer sequences, short reads, odd-length RX/TX, timeout dequeue before and after command submission, TID mismatch, latency warnings, programming errors, FIFO reset recovery, segmented IBI payloads, no-slot IBI drops, unknown IBI addresses, and suspend/resume threshold reinitialization.
