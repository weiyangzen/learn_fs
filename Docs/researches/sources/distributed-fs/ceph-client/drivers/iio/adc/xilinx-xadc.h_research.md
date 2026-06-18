# sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc.h

## Purpose
This header is the shared internal contract for the Xilinx XADC driver. It declares the event helper APIs, defines `struct xadc` and `struct xadc_ops`, provides mutex-aware register access wrappers, and centralizes hardmacro register, configuration, alarm, and threshold constants.

## Important APIs, Types, And Functions
`struct xadc` is the driver-private state shared across the core and event files. It contains MMIO base, clock, selected ops, threshold cache, temperature hysteresis, alarm mask, buffer data pointer, trigger pointers, external mux mode, Zynq-specific interrupt masking state, delayed work, mutex, spinlock, and completion. `enum xadc_external_mux_mode` represents no/single/dual mux configuration. `enum xadc_type` distinguishes Series 7 and UltraScale scaling/channel behavior. `struct xadc_ops` abstracts register read/write, setup, alarm update, dclk-rate query, interrupt handler, feature flags, type, and temperature conversion constants.

Inline helpers `_xadc_read_adc_reg()` and `_xadc_write_adc_reg()` assert the mutex is held and call the selected ops. Public `xadc_read_adc_reg()` and `xadc_write_adc_reg()` acquire and release the mutex. The macro block defines ADC result registers, max/min history registers, sequencer/input-mode/threshold registers, `CONF0/CONF1/CONF2` bitfields, power-down bits, alarm masks, and threshold indexes.

## Control Flow
The header itself has no runtime control flow, but it shapes the core: all variant register access is routed through `xadc_ops`, and event code uses the threshold/alarm constants to translate userspace ABI operations into hardware registers. The lock-asserting helper split is important because some operations update multiple registers under one mutex and need to avoid nested locking.

## State And Persistence
No state is allocated here, but the state layout controls persistence and synchronization semantics. Threshold and alarm state are runtime memory mirrors of hardware registers. `mutex` protects ADC register transactions and event configuration; `spinlock_t lock` protects IRQ-level register masking paths; `completion` synchronizes Zynq FIFO responses.

## Dependencies And Integration Points
The header depends on Linux interrupt, mutex, and spinlock declarations plus forward declarations for IIO, clock, and platform-device types. It is included by `xilinx-xadc-core.c` and `xilinx-xadc-events.c` and must remain aligned with Xilinx hardmacro documentation and the channel maps in the core.

## Risks And Test Signals
The main risk is that constant or bitfield changes affect both direct reads and event handling. `XADC_CONF1_ALARM_MASK` and threshold offsets must match hardware layout and event code assumptions. Tests are indirect: build coverage for both source files, lockdep coverage for `_xadc_*` helpers, event ABI tests for every alarm mask, and buffered/direct register-access tests across Series 7 and UltraScale variants.
