## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ssv_dnp.c

Purpose: Generic legacy Comedi DIO driver for SSV Embedded Systems DIL/Net-PC 1486 devices. It exposes 20 digital I/O channels backed by indexed chip setup/control registers.

Important APIs, types, and functions: Register constants name the chip setup index/data ports and port A/B/C mode/data registers. `dnp_dio_insn_bits()` writes and reads the packed 20-bit DIO state across ports A, B, and the high nibble of port C. `dnp_dio_insn_config()` maps Comedi per-channel input/output configuration into the unusual mode-register bit layout. `dnp_attach()` creates the single DIO subdevice and initializes all ports as input; `dnp_detach()` restores that input state.

Control flow and state: The driver does not reserve I/O ports because the addresses are fixed system resources. DIO writes update port A and B directly and preserve the low nibble of port C while writing output bits to the high nibble. Reads reconstruct `data[1]` from the same register layout. Direction config reads the current mode register, sets or clears the relevant bit, and writes it back; for port C it maps logical channels 16-19 to every other bit of PCMR.

Dependencies and integration: It uses `linux/comedi/comedidev.h`, port I/O, Comedi DIO helpers, `range_digital`, and `module_comedi_driver()`.

Risks and test signals: Fixed I/O registers overlap system control ports by design, so accidental use on unsupported hardware is risky. Port C has noncontiguous mode bits and data bits shifted into the upper nibble, making off-by-one errors likely. Test signals should include attach/detach all-input reset, per-channel direction for A/B/C, preservation of unrelated port C bits, readback packing, and masked writes through `comedi_dio_update_state()`.
