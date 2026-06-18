# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tegra-bpmp.c

Purpose: provides an I2C adapter whose transfers are executed by NVIDIA Tegra BPMP firmware rather than directly by Linux-controlled I2C registers. It serializes Linux `i2c_msg` arrays into BPMP MRQ_I2C requests and deserializes firmware read responses.

Important APIs/types/functions: `struct tegra_bpmp_i2c` stores adapter, device, BPMP handle, and firmware bus ID. `tegra_bpmp_xlate_flags()` maps Linux I2C flags to serial-I2C firmware flags. `tegra_bpmp_serialize_i2c_msg()` and `tegra_bpmp_i2c_deserialize()` implement the wire format. `tegra_bpmp_i2c_xfer_common()` is used by normal and atomic hooks.

Control flow: probe gets the parent BPMP object, reads `nvidia,bpmp-bus-id`, initializes adapter fields, and registers the adapter. A transfer first checks serialized TX and expected RX sizes against BPMP ABI buffer limits. It then builds a request with little-endian address/flags/length headers and write payloads, sends it through `tegra_bpmp_transfer()` or `_atomic()`, maps BPMP firmware errors to Linux errno, validates response read length, copies read blocks back into each read message, and returns `num`.

State and persistence: there is almost no controller-local state beyond bus ID and BPMP pointer. Firmware owns actual hardware state, locking, timing, power, and bus recovery. Per-transfer request/response structs are stack-local.

Dependencies and integration: depends on Tegra BPMP ABI headers, parent BPMP device data, OF compatible `nvidia,tegra186-bpmp-i2c`, platform devices, and Linux I2C core. It advertises I2C, SMBus emulation, 10-bit addressing, protocol mangling, and NOSTART.

Risks: message size validation must match BPMP ABI limits; otherwise firmware buffers would be overrun. The deserialize path requires total read length to match firmware response exactly. All bus behavior is delegated to firmware, so Linux-side observability and recovery are limited. Unsupported or newly added Linux flags would need explicit translation.

Test signals: serialization for read/write/mixed messages, every supported flag translation, oversized TX/RX rejection, firmware return mapping for EAGAIN/ETIMEDOUT/ENXIO/unknown errors, atomic transfer path, and probe without parent BPMP or bus ID.
