# sources/distributed-fs/ceph-client/sound/soc/codecs/ntpfw.c

Purpose: provides a shared firmware loader for Neofidelity amplifier drivers. It requests a firmware file, validates a big-endian magic header, parses variable chunks, and sends chunk payloads over I2C in fixed step sizes.

Important APIs, types, and functions: packed `struct ntpfw_header` contains a big-endian magic value. Packed `struct ntpfw_chunk` contains a big-endian payload length, an I2C transfer step, and payload bytes. Internal helpers are `ntpfw_verify()`, `ntpfw_verify_chunk()`, and `ntpfw_send_chunk()`. Public exported API is `ntpfw_load(struct i2c_client *i2c, const char *name, u32 magic)`.

Control flow: `ntpfw_load()` calls `request_firmware()`, validates the image header, then iterates from the first chunk after the header until no bytes remain. Each chunk must have step 2 or 5, length not exceeding remaining firmware bytes, and length divisible by step. The sender loops over payload bytes and calls `i2c_master_send()` with exactly `step` bytes. Any short send returns `-EIO`; negative I2C errors are propagated. Firmware is always released through the `done` path.

State and persistence: the helper holds no persistent state. All state is in the firmware buffer and local parsing pointers. Calling amplifier drivers decide whether missing firmware is fatal and when to reload after reset or resume.

Dependencies and integration points: depends on Linux firmware loader, I2C core, endian helpers, module exports, and `ntpfw.h`. It is used by `ntp8835.c` and `ntp8918.c` with different firmware names and magic values.

Risks: chunk-size validation allows `chunk_size == buf_size`, but later pointer arithmetic subtracts `chunk_size + sizeof(*chunk)` from `leftover`; malformed images can underflow `size_t` if there is no room for the chunk header plus data. The image format trusts packed unaligned casts. Only step sizes 2 and 5 are supported. Errors log but do not identify chunk offsets.

Test signals: unit or fault-injection tests with too-small images, bad magic, invalid steps, non-divisible lengths, short I2C writes, exact-boundary chunks, multiple chunks, and firmware release on every error path. Integration tests should confirm NTP8835/NTP8918 firmware blobs are accepted and sent in the expected transfer widths.
