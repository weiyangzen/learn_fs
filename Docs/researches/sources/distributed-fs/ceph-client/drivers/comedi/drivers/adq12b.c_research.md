# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adq12b.c Research

Provides a legacy ISA-style Comedi driver for the MicroAxial ADQ12-B acquisition/control card. It exposes synchronous analog input, 5 digital inputs, and 8 digital outputs; pacer hardware is documented but not supported.

`struct adq12b_private` caches `last_ctreg` so channel/range changes can be avoided unless necessary. `adq12b_attach()` validates and requests the configured I/O range, allocates private data and three subdevices, and chooses AI range/reference shape from configuration options. `adq12b_ai_insn_read()` programs channel/range, waits for mux settling, triggers conversions through ADC register reads, and polls `adq12b_ai_eoc()`. DIO paths are `adq12b_di_insn_bits()` and `adq12b_do_insn_bits()`.

The attach path is entirely manual through Comedi config options: base address, bipolar/unipolar mode, and single-ended/differential mode. AI reads update the CTREG only when the requested channel/range changes, then perform repeated conversion/poll/read cycles. DO writes iterate over changed bits from `comedi_dio_update_state()` and write encoded channel/value commands to the output buffer register. Runtime state is limited to cached CTREG and Comedi subdevice output state.

Dependencies are legacy `comedidev`, raw I/O port access, `comedi_check_request_region()`, `comedi_timeout()`, and `module_comedi_driver()`. Risks include stale mux/range state, timeout on EOC polling, and bit-by-bit output register programming. Tests should verify valid base-address stepping, range table selection, differential channel count, mux settle behavior after channel changes, repeated AI retriggering, DI masking to five bits, and DO writes only for changed output bits.
