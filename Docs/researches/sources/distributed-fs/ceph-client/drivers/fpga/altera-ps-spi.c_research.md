## sources/distributed-fs/ceph-client/drivers/fpga/altera-ps-spi.c

Purpose: this FPGA manager programs Altera FPGAs over passive-serial SPI using `nconfig`, `nstat`, and optional `confd` GPIOs. It supports Cyclone V compatible timing and Arria 10 timing.

Important APIs and functions: `struct altera_ps_data` captures per-family timing values. `struct altera_ps_conf` stores GPIO descriptors, SPI device, selected timing data, image flags, and manager name. Manager callbacks are `altera_ps_state()`, `altera_ps_write_init()`, `altera_ps_write()`, and `altera_ps_write_complete()`. `rev_buf()` bit-reverses firmware data unless the image is already LSB-first.

Control flow: probe selects match data, acquires `nconfig` output, `nstat` input, optional `confd` input, and registers a devm FPGA manager. Programming rejects partial reconfiguration, pulses `nconfig`, waits for `nstat` to indicate reset and then readiness, delays for timing requirements, streams the bitstream over SPI in 4 KiB chunks with bit reversal when needed, checks `nstat` and optional `confd`, and sends one dummy byte to provide extra DCLK edges for user mode entry.

State and persistence: software state includes last image flags and static per-family timing. Hardware state is represented by GPIO lines and FPGA configuration state. The write path mutates the firmware buffer in-place during bit reversal.

Dependencies and integration: it depends on SPI, GPIO descriptors, OF/SPI device IDs, `BITREVERSE`, and the FPGA manager framework. Firmware images are expected in binary RBF format.

Risks: in-place bit reversal means a shared or reused firmware buffer is modified. `altera_ps_state()` only distinguishes reset when `nstat` is high, otherwise unknown. Timing loops depend on board GPIO polarity conventions matching descriptor names. Optional `confd` absence is only a warning, reducing final configuration confidence.

Test signals: exercise Cyclone/Stratix-compatible and Arria 10 timing paths, partial-reconfig rejection, `nstat` stuck-high/stuck-low failures, optional `confd` failure, SPI write errors, LSB-first and bit-reversed image flags, and odd chunk sizes.
