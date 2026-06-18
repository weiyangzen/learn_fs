# sources/distributed-fs/ceph-client/drivers/misc/lattice-ecp3-config.c

## Purpose
`lattice-ecp3-config.c` configures supported Lattice ECP3 FPGAs over SPI using the firmware file `lattice-ecp3.bit`. It identifies the FPGA, clears configuration memory, streams the bitstream, disables writing, and checks the DONE bit.

## Important APIs, types, and functions
`struct fpga_data` carries a completion used to wait for asynchronous firmware loading on remove. `struct ecp3_dev` lists supported reversed JTAG IDs. `firmware_load` contains the full configuration sequence. `lattice_ecp3_probe` allocates state and calls `request_firmware_nowait`; `lattice_ecp3_remove` waits for completion.

## Control flow
Probe requests firmware asynchronously and returns after registration. The callback rejects missing or zero-length firmware, sends READ_ID, validates the JEDEC ID, reads status, allocates a transmit buffer with WRITE_INC header plus firmware data, sends REFRESH, WRITE_EN, and CLEAR, polls status up to five seconds for the CLEARED value, writes the bitstream, sends WRITE_DIS, rereads status, reports whether DONE is set, releases firmware, frees the buffer, and completes `fw_loaded`.

## State and persistence
Driver state is minimal and devm-managed. Hardware state changes are persistent in the FPGA configuration until power cycle or reconfiguration. The completion protects remove from racing the asynchronous callback.

## Dependencies and integration points
The driver depends on SPI transfers, request_firmware, unaligned big-endian helpers, and module firmware loading. It binds SPI IDs `ecp3-17` and `ecp3-35`.

## Risks
SPI transfer return values are mostly not checked in the callback, so bus errors could be reported only as failed status/DONE checks. The status comparison for CLEARED expects an exact value, which may be brittle if other status bits are set. Asynchronous firmware loading means remove ordering relies on completion.

## Test signals
Validation should cover firmware missing, zero-size firmware, unsupported JEDEC ID, clear timeout, successful DONE set, DONE not set, and remove during firmware load. SPI traces should show the expected command ordering.
