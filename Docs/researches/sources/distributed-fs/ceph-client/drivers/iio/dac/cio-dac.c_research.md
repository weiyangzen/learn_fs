## sources/distributed-fs/ceph-client/drivers/iio/dac/cio-dac.c

Purpose: ISA I/O-port IIO driver for Measurement Computing CIO-DAC16, CIO-DAC08, and PC104-DAC06 boards. It exposes 16 voltage-output DAC channels with 12-bit raw writes.

Important APIs/types/functions: `struct cio_dac_iio` holds the `regmap`. `cio_dac_read_raw()` and `cio_dac_write_raw()` implement `IIO_CHAN_INFO_RAW`. `cio_dac_probe()` claims the configured I/O port region, maps it, initializes an I/O-port regmap, and registers the IIO device. The module parameter `base[]` provides board addresses for `module_isa_driver()`.

Control flow: Each configured ISA base address becomes an ISA device instance. Probe requests 32 bytes, maps them, creates a 16-bit regmap with two-byte stride, and registers a direct-mode IIO device using fixed channels. Reads and writes compute `base + channel * 2` and go through regmap.

State and persistence: The driver has no software cache. All registers are marked precious because on some board jumper settings reading a DAC register can trigger the output transfer. Hardware output persists only while the board remains powered/configured.

Dependencies and integration points: Depends on the ISA bus helper, module hardware parameters, IIO core, and regmap configured for I/O ports. It integrates through sysfs raw DAC attributes and legacy ISA port resource reservation.

Risks and test signals: The main risks are incorrect `base` parameters, failed I/O-port reservation, and side effects from reads on XFER-jumper boards. Tests should validate 0..4095 bounds, one channel stride per output, probe failure on busy ports, and actual board behavior for read-triggered transfers.
