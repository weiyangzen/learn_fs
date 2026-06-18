# sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc-core.c

## Purpose
This file is the core Xilinx XADC/System Monitor IIO driver. It supports Zynq hard XADC and AXI XADC/System Management Wizard variants, exposing internal temperature, supply voltages, VP/VN, VREF, VAUX channels, sampling-frequency control, threshold events, and buffered acquisition for AXI-backed variants.

## Important APIs, Types, And Functions
The implementation is structured around `struct xadc` from `xilinx-xadc.h` and variant-specific `struct xadc_ops`. `xadc_zynq_ops` communicates through the Zynq command/data FIFOs and level-sensitive interrupt masking. `xadc_7s_axi_ops` and `xadc_us_axi_ops` use direct AXI register windows, optional IRQs, and buffered acquisition. Channel templates are `xadc_7s_channels` and `xadc_us_channels`; firmware parsing duplicates and prunes them based on `xlnx,channels`, `xlnx,external-mux`, optional bipolar flags, and IRQ availability.

Key functions include Zynq FIFO register accessors (`xadc_zynq_read_adc_reg()`, `xadc_zynq_write_adc_reg()`), AXI accessors, interrupt handlers, alarm update functions, `xadc_read_raw()` and `xadc_write_raw()` for IIO data paths, `xadc_read_samplerate()` and `xadc_write_samplerate()` for `CONF2` divisor handling, `xadc_preenable()` and `xadc_postdisable()` for sequencer setup around buffers, `xadc_trigger_handler()` for buffered sample reads, and `xadc_parse_dt()`/`xadc_probe()` for integration.

## Control Flow
Probe selects ops from compatible data, obtains an optional IRQ subject to variant flags, allocates state, initializes locks/completion/delayed work, maps MMIO, parses firmware channels and external mux config, optionally sets up triggered buffers and AXI triggers, enables the clock, clamps buffered sample rate to 150 kSPS, requests the IRQ, runs variant setup, snapshots all threshold registers, writes `CONF0`, programs input bipolar masks, switches to non-buffered continuous sequencer mode with `xadc_postdisable()`, and registers IIO.

Direct reads fail with `-EBUSY` when a buffer is active, read the channel address through the ops layer, shift/sign-extend according to the channel scan type, and return scale/offset/sample-rate metadata. Buffer enable programs scan masks into sequencer registers, chooses continuous versus simultaneous/independent mode based on selected VAUX channels and external mux mode, powers ADC-B as needed, and enables sequencer mode. The trigger handler reads each active channel register and pushes the packed buffer.

## State And Persistence
Runtime state includes threshold cache, temperature hysteresis, enabled alarm mask, buffer data allocation, active trigger pointers, external mux mode, Zynq masked-alarm/intmask fields, completion state, mutex, and spinlock. Register state is restored by setup and postdisable, but not persisted outside runtime. Zynq register access serializes command FIFO operations with spinlocks and completions; generic ADC register access is protected by the XADC mutex.

## Dependencies And Integration Points
The driver depends on platform firmware compatibles `xlnx,zynq-xadc-1.00.a`, `xlnx,axi-xadc-1.00.a`, and `xlnx,system-management-wiz-1.3`, MMIO, clocks, optional IRQs, IIO events, IIO triggered buffers, and `xilinx-xadc-events.c` for event ABI helpers. It integrates with external mux firmware properties and child channel definitions. Userspace sees raw, scale, offset, sampling frequency, threshold event configuration, and optional buffer triggers named for `convst` and `samplerate`.

## Risks And Test Signals
The major operational risk is interrupt load: the driver clamps sampling to 150 kSPS because the hardware lacks a FIFO. Zynq threshold IRQs are level-sensitive and require delayed unmask logic; broken masking can produce interrupt storms. `xadc_parse_dt()` tolerates invalid child channel `reg` by skipping them, so firmware mistakes can silently reduce channel coverage. Tests should cover all three compatibles, with and without IRQ, external mux modes, bipolar child channels, sample-rate clamp and divisor rounding, direct reads blocked by active buffers, buffer scan modes across lower/upper VAUX groups, threshold and hysteresis writes, Zynq FIFO timeout paths, AXI EOS trigger polling, delayed alarm unmask, and UltraScale temperature scale/offset.
