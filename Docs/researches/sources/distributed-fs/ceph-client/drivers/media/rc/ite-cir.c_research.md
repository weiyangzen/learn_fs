# sources/distributed-fs/ceph-client/drivers/media/rc/ite-cir.c

## Purpose

`ite-cir.c` is the Linux rc-core PNP driver for ITE Consumer IR transceivers, covering direct IT87-style CIR blocks and IT8512-based bridges exposed as ITE8708 or ITE8709. It receives raw IR samples, decodes hardware FIFO bytes into `ir_raw_event` pulse/space durations, supports IR transmit through run-length encoded FIFO writes, and registers an `rc_dev` with receive, transmit, carrier, duty-cycle, idle, open, and close callbacks.

## Important APIs, Types, and Functions

- Module parameters `sample_period` and `model_number` tune the sample clock and optionally override PNP model autodetection.
- `ite_decode_bytes()` converts little-endian bit runs from RX FIFO bytes into pulse/space events with `ir_raw_event_store_with_filter()` and `ir_raw_event_handle()`.
- `ite_set_carrier_params()`, `ite_get_carrier_freq_bits()`, and `ite_get_pulse_width_bits()` translate rc-core carrier/duty settings into chip-specific register fields through the active `ite_dev_params` backend.
- `ite_cir_isr()` handles RX FIFO, RX overrun, and TX FIFO-space interrupts under `dev->lock`, deliberately dropping the lock before handing received data to rc-core.
- `ite_tx_ir()` is the transmit path; it disables RX, encodes alternating pulse/space durations into 7-bit run-length bytes, blocks on `tx_queue` when the TX FIFO is full, waits for the remaining FIFO time, restores RX parameters, and wakes `tx_ended`.
- Hardware backend functions implement IT87 direct I/O, IT8708 banked IT8512 access, and IT8709 SRAM/microcontroller bridge access.
- `ite_probe()`, `ite_remove()`, `ite_suspend()`, `ite_resume()`, and `ite_shutdown()` bind the PNP device, register rc-core state, claim I/O and IRQ resources, and handle power transitions.

## Control Flow

Probe allocates `struct ite_dev` and `struct rc_dev`, selects a model from `ite_ids[]` or the `model_number` override, validates PNP port and IRQ resources, initializes locks and wait queues, programs default carrier and FIFO registers, fills rc-core callbacks, registers the `rc_dev`, claims the I/O region, and finally requests the shared IRQ. Opening the rc device enables RX; closing waits for any in-flight transmit and disables the backend.

Receive flow starts in `ite_cir_isr()`: the backend reports interrupt causes, RX overflow is signaled to rc-core, FIFO bytes are read into a 32-byte stack buffer, and the lock is dropped while the raw event layer receives decoded pulse/space events. Transmit flow starts from rc-core `tx_ir`, switches the device into transmit mode, updates carrier registers, disables RX, writes RLE bytes to the TX FIFO, sleeps on an interrupt-driven wait queue when fewer than eight slots are available, delays for the final queued duration, then re-enables RX and wakes close/suspend waiters.

## State and Persistence Behavior

Driver-owned state lives in `struct ite_dev`: the PNP and rc-core objects, spinlock, `transmitting` flag, two wait queues, RX carrier range, TX carrier/duty settings, I/O base, IRQ, and the selected immutable backend descriptor. Hardware state persists in CIR registers and FIFOs until reset, shutdown, suspend, or backend disable. The driver does not write disk state; module parameters and userspace rc-core configuration determine behavior across loads.

## Dependencies and Integration Points

The file depends on PNP discovery, port I/O helpers (`inb`/`outb`), IRQ infrastructure, wait queues, rc-core raw-event APIs, input IDs, and constants from `ite-cir.h`. It integrates with rc-core as an `RC_DRIVER_IR_RAW` device with `allowed_protocols = RC_PROTO_BIT_ALL_IR_DECODER` and default map `RC_MAP_RC6_MCE`. It also consumes Linux PCI vendor IDs for ITE input identification and relies on the keymap and decoder infrastructure to convert raw events into user-visible key events.

## Risks and Edge Cases

The TX path calls `get_tx_used_slots()` while waiting without holding the spinlock, which the source comments acknowledge as an assumption. `wait_event_interruptible()` return values are ignored in TX, close, and suspend paths, so signal interruption does not abort or report partial progress. The IT8709 SRAM bridge clears RX FIFO state through a protocol described as inherently racy, making overflow and lost samples plausible under load. Carrier calculations clamp ranges but accept arbitrary module/user inputs; invalid duty-cycle values from callers would distort pulse width selection. Resource teardown must respect the order `free_irq`, `release_region`, `rc_unregister_device`, and `kfree` to avoid IRQ callbacks touching freed state. Incorrect model override can select the wrong register backend and write unrelated I/O ports.

## Test Signals

Build coverage should include the PNP driver and all three backend families. Runtime tests should probe each supported PNP ID, open/close the rc device repeatedly, receive known NEC/RC5/RC6 remotes through raw decoders, inject or observe RX overrun handling, transmit long pulse trains that exceed the 32-byte FIFO, verify `s_tx_carrier`, `s_tx_duty_cycle`, and `s_rx_carrier_range`, suspend/resume during idle and after TX, unload while no users are active, and exercise the `model_number` override only on controlled hardware.
