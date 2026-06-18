## sources/distributed-fs/ceph-client/drivers/iio/dac/dpot-dac.c

Purpose: Creates a synthetic voltage-output DAC from an IIO digital potentiometer channel wired as a divider from a `vref` regulator. It maps voltage-DAC raw writes to the underlying resistance channel raw value.

Important APIs/types/functions: `struct dpot_dac` stores the `vref` regulator, consumed `dpot` IIO channel, and computed maximum resistance. `dpot_dac_read_raw()`, `dpot_dac_write_raw()`, and `dpot_dac_read_avail()` proxy and scale the backing channel. `dpot_dac_channel_max_ohms()` derives full-scale resistance from raw max and channel scale. Probe validates that the consumed channel type is `IIO_RESISTANCE`.

Control flow: Probe allocates one IIO voltage output channel, gets `vref`, gets an IIO channel named `dpot`, validates type, computes max ohms, enables the regulator, and registers the device. Raw reads/writes are direct IIO consumer calls. Scale is calculated from the dpot resistance scale and regulator voltage, preserving integer, fractional, and log2 fractional representations.

State and persistence: Only `max_ohms` is cached. The current output state lives in the upstream dpot provider. The regulator is explicitly enabled at probe and disabled on remove.

Dependencies and integration points: Depends on IIO consumer APIs, regulator APIs, platform device/OF compatible `dpot-dac`, and the upstream digital potentiometer driver. It is an integration shim for board designs rather than a physical DAC driver.

Risks and test signals: Scale arithmetic is the key risk because it combines regulator voltage and resistance units across IIO return formats. Test with dpot providers returning `IIO_VAL_INT`, `IIO_VAL_FRACTIONAL`, and `IIO_VAL_FRACTIONAL_LOG2`; validate raw available passthrough, regulator cleanup on registration failure, and rejection of non-resistance input channels.
