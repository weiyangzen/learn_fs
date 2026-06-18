<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ps2-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/ps2-gpio.c

## Purpose
`ps2-gpio.c` is a GPIO bit-banged PS/2 serio bus driver. It samples PS/2 clock falling-edge interrupts and the data GPIO to receive bytes, optionally drives open-drain clock/data GPIOs to transmit bytes, and exposes a platform/DT-backed serio port.

## Important APIs, types, and functions
- `struct ps2_gpio_data` stores the device, serio port, RX/TX mode, open-drain GPIOs, write-enable flag, IRQ, IRQ timestamps, RX bit state, TX bit state, completion, mutex, and delayed work.
- `ps2_gpio_open()`/`ps2_gpio_close()` enable and disable the IRQ and flush pending TX work.
- `ps2_gpio_write()` serializes process-context writes with a mutex, starts TX, and waits for a completion; atomic-context writes start TX without waiting.
- `__ps2_gpio_write()` disables IRQs, pulls clock low, switches to TX mode, stores the byte, and schedules delayed work to begin the host request-to-send sequence.
- `ps2_gpio_irq_rx()` validates PS/2 timing, samples start/data/parity/stop bits, reports parity, filters ACK/NACK when write support is disabled, and requests resend on errors.
- `ps2_gpio_irq_tx()` advances host-to-device bits, releases the data line for stop, samples ACK, completes writes, or retries on timeout/NACK.
- `ps2_gpio_get_props()` obtains open-drain `data` and `clk` GPIOs and optional `write-enable`.
- `ps2_gpio_probe()` validates fast GPIOs, requests a non-threaded no-auto-enable IRQ, initializes TX work/completion/mutex, and registers the serio port.

## Control flow
Probe creates driver and serio state, reads platform properties, rejects GPIOs that can sleep, gets the IRQ, installs `ps2_gpio_irq()` with `IRQF_NO_THREAD | IRQF_NO_AUTOEN`, initializes RX mode and TX state, then registers the port. Open enables the IRQ. In RX mode, each IRQ samples one bit and completes a byte after the stop bit. In TX mode, the delayed work releases the clock after the host inhibit interval, then each IRQ drives the next bit until the ACK bit completes the transfer. Remove unregisters the serio port.

## State and persistence
The driver stores transient bit counters, current byte, timestamps, mode, and TX completion state. It does not persist settings. GPIO direction and IRQ enable state change dynamically during open, close, RX, and TX.

## Dependencies and integration points
It depends on gpiolib consumer APIs, platform/OF properties, hard IRQ timing, delayed work, completions, mutexes, ktime, and the serio core. The external GPIO wiring must support open-drain PS/2 signaling and low-latency GPIO reads/writes.

## Risks
- Timing is tight: GPIOs connected via sleeping controllers are rejected, but interrupt latency can still cause missed bits.
- RX error handling sends `RESEND` even when errors are caused by local timing, which may loop if write support or wiring is faulty.
- TX retry is recursive through `__ps2_gpio_write()` from IRQ context, requiring careful state consistency.
- Process-context writes can wait up to 10 seconds.
- Parity errors are tolerated and forwarded when write support is enabled but cause resend when write support is disabled.

## Test signals
- Build with GPIO, OF, and serio support.
- DT/property tests should cover missing GPIOs, sleeping GPIO rejection, missing IRQ, write-enable false/true, and remove cleanup.
- Hardware tests should cover RX timing limits, parity and stop-bit errors, ACK/NACK TX completion, resend behavior, IRQ disabled on close, and concurrent write serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ps2-gpio.c -->
