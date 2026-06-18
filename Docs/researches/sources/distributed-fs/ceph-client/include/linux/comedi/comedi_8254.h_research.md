# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_8254.h

Purpose: This header provides generic Comedi support for Intel 8254-style timer/counter devices, including register definitions, oscillator constants, state storage, access callbacks, timer programming helpers, and allocation helpers for I/O-port or MMIO-backed counters.

Important APIs/types/functions: It defines oscillator base constants from 10 MHz through 1 kHz, access sizes `I8254_IO8/16/32`, counter/control register offsets and control word helpers, `I8254_MAX_COUNT`, callback typedef `comedi_8254_iocb_fn`, and `struct comedi_8254` containing access callback/context, oscillator base, divisors, next divisors, clock/gate sources, busy flags, and optional instruction config callback. APIs include status/read/write, mode/load, pacer enable, divisor update, ns-to-timer conversion for single and cascaded timers, busy marking, subdevice init, `comedi_8254_io_alloc`, and `comedi_8254_mm_alloc`.

Control flow: Drivers allocate an 8254 object for I/O or MMIO, initialize a Comedi subdevice with it, convert desired nanosecond periods to divisors, load modes/counts, and enable/disable cascaded pacers. Register access flows through the callback so bus-specific access is abstracted.

State and persistence behavior: The struct caches current and next divisors, source selections, and busy state, while hardware counters hold programmed mode/count. I/O allocation returns `-ENXIO` when `CONFIG_HAS_IOPORT` is unavailable.

Dependencies and integration points: It includes types, errno, and err helpers and integrates with Comedi subdevices, instruction config paths, pacer timing for acquisition, I/O port access, and MMIO access.

Risks: Timer divisor zero maps to `0x10000`, which must be handled intentionally. Wrong oscillator base or access size produces incorrect sample timing. Cascaded counter ordering matters. Busy flags must prevent conflicting ownership of counters.

Test signals: Comedi driver tests for pacer frequency, mode programming, I/O-port-disabled builds, MMIO-backed devices, divisor conversion edge cases, and acquisition timing validate behavior.
