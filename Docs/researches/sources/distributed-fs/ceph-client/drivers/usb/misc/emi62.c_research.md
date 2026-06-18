# sources/distributed-fs/ceph-client/drivers/usb/misc/emi62.c

Purpose: Firmware-loader-only USB driver for Emagic EMI 6|2m devices. It is structurally similar to `emi26.c`, but selects `emi62/spdif.fw` at compile time through `SPDIF` and otherwise would use `emi62/midi.fw`.

Important APIs and types: `emi62_writememory()`, `emi62_set_reset()`, `emi62_load_firmware()`, `emi62_probe()`, and firmware files `emi62/loader.fw`, `emi62/bitstream.fw`, and `FIRMWARE_FW`. It uses EZ-USB reset register `CPUCS_REG` and Anchor vendor memory load commands.

Control flow: probe calls firmware load and returns `-EIO` so ownership is handed to the real driver. Load asserts reset, loads the FPGA helper, releases reset, streams the FPGA bitstream, reloads helper code, releases reset, loads external final firmware, asserts reset, loads internal-address final records, releases reset, and returns positive `1` on success.

State and persistence: no driver state is registered after probe; all effects are on device RAM/FPGA state. Risks include hard-coded SPDIF/MIDI selection, `ANCHOR_LOAD_EXTERNAL` used for internal records in the final pass, no exact-length control-transfer validation, and intentionally failed probe semantics. Test signals include firmware request paths, successful post-load handoff, device timing delays, and failure logs for each control-transfer phase.
