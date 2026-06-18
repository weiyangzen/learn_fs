# sources/distributed-fs/ceph-client/drivers/media/rc/ite-cir.h

## Purpose

`ite-cir.h` is the private hardware contract for the ITE CIR driver. It defines the shared device model, backend operation table, FIFO/IRQ constants, carrier-frequency conversion limits, transmit RLE encoding, and register offsets/bit masks for IT87, IT8512, ITE8708, and ITE8709 access paths. The header has no executable code beyond simple conversion macros; it gives `ite-cir.c` the exact fields needed to program several related hardware generations through one common driver.

## Important APIs, Types, and Functions

- `struct ite_dev_params` describes one supported model, including I/O region size/resource number and function pointers for IRQ cause detection, RX enable/idle/disable, RX FIFO readout, TX interrupt control, TX FIFO occupancy/write, hardware disable/init, and carrier programming.
- `struct ite_dev` stores PNP/rc-core pointers, `spinlock_t lock`, `transmitting`, TX wait queues, carrier and duty settings, I/O/IRQ resources, and the selected `ite_dev_params`.
- Common constants define FIFO sizes, software interrupt cause bits, baud divisor, low/high carrier ranges, default carrier, demodulator tolerance units, high-frequency carrier selectors, transmit pulse-width selectors, and TX byte layout (`ITE_TX_SPACE`, `ITE_TX_MAX_RLE`, `ITE_TX_RLE_MASK`).
- Register blocks define direct IT87 offsets and masks, generic IT85 CIR register fields, ITE8708 bank-select mappings, and ITE8709 SRAM bridge offsets and request modes.

## Control Flow

The header itself has no control flow. At runtime, `ite_probe()` selects one `ite_dev_params` instance and all driver operations dispatch through its function pointers. The macros and bit masks are used by backend helpers to initialize hardware, identify pending IRQ causes, drain RX FIFOs, feed TX FIFOs, clear FIFO state, toggle interrupts, and program carrier/demodulator parameters.

## State and Persistence Behavior

No state is allocated or persisted by this header. It defines the in-memory shape of driver state and the register-backed hardware state that `ite-cir.c` mutates. The fields in `struct ite_dev` persist for the lifetime of a bound PNP device; hardware register values persist until reset, disable, suspend, resume reinitialization, or module unload.

## Dependencies and Integration Points

The declarations depend on kernel types made available before inclusion, including `struct pnp_dev`, `struct rc_dev`, `spinlock_t`, wait queues, `u8`, and `bool`. The header is tightly coupled to `ite-cir.c`; the operation table mirrors every backend hook implemented there. It also bridges ITE hardware documentation into rc-core concepts such as sample periods, carrier ranges, pulse widths, and raw IR FIFO data.

## Risks and Edge Cases

Register constants are untyped preprocessor values, so a wrong offset, mask, or bank-select bit can compile cleanly while corrupting the wrong I/O register. The IT8708 mapping is based on reverse-engineered bank layout with some unknown registers, and the IT8709 SRAM protocol is explicitly reverse engineered, so those constants carry higher hardware-compatibility risk than direct IT87 definitions. Comments note that most backend operations must be called with the spinlock held, but the type system cannot enforce that contract. The `rx_high_carrier_freq` comment labels it as TX high carrier frequency, which can confuse maintenance even though the field is used as the high end of the RX carrier range.

## Test Signals

Useful validation includes compile coverage of `ite-cir.c`, static review that every backend fills all `ite_dev_params` hooks, hardware smoke tests for each PNP ID, register read/write tracing during init/disable/RX/TX, carrier-frequency tests across low and high ranges, and regression tests that RX FIFO, TX FIFO, bank switching, and SRAM bridge constants still match known working hardware.
