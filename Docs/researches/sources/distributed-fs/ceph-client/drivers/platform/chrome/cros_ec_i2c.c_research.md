# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_i2c.c

Purpose: I2C transport driver for ChromeOS EC, supporting legacy protocol v2 and packet protocol v3.

Important APIs, types, and functions: `struct ec_host_request_i2c` and `struct ec_host_response_i2c` define the v3 I2C framing. `cros_ec_pkt_xfer_i2c()` sends v3 packets using core `cros_ec_prepare_tx()`. `cros_ec_cmd_xfer_i2c()` sends legacy v2 packets with command/version/length/checksum framing. Probe allocates a core EC device and assigns both transfer callbacks.

Control flow: v3 transfer sizes EC input/output buffers, writes protocol byte `0xda`, temporarily advances `ec_dev->dout` so `cros_ec_prepare_tx()` writes after the protocol byte, performs a combined I2C write/read, validates result, header length, response size, and checksum, then copies payload to `msg->data`. It returns `-EPROTONOSUPPORT` if a v2 EC responds to protocol byte as invalid with zero packet length. v2 transfer allocates temporary buffers, computes additive checksum, performs combined transfer, checks result and response checksum, and returns payload length. Probe sets `priv`, IRQ, callbacks, and phys name, then calls `cros_ec_register()`.

State and persistence: per-device state is the core EC object and I2C client pointer. v3 uses shared core buffers; v2 allocates per command. No transport-specific persistent hardware state.

Dependencies and integration points: I2C core, OF compatible `google,cros-ec-i2c`, ACPI ID `GOOG0008`, core Chrome EC lifecycle, and PM sleep helpers. IRQ comes from the I2C client.

Risks and edge cases: v3 response reads a fixed `insize + header` length; devices returning shorter transfers depend on adapter behavior. v2 path uses dynamic allocation for each command. I2C checksum logic assumes full buffers initialized by EC. Reboot command sleeps after transfer in both paths. PM ops use late suspend/resume wrappers around core full suspend/resume.

Test signals: protocol negotiation from v3 to v2 fallback, command transfer with payload boundaries, checksum failure handling, EC reboot delay, IRQ event delivery, OF/ACPI probe, and suspend/resume host-sleep behavior.
