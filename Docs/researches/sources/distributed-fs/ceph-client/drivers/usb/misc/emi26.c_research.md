# sources/distributed-fs/ceph-client/drivers/usb/misc/emi26.c

Purpose: Firmware-loader-only USB driver for Emagic EMI 2|6 devices before their real audio firmware is active. It downloads EZ-USB loader, FPGA bitstream, and final firmware, then deliberately returns an error from probe so the functional audio driver can bind after re-enumeration or firmware activation.

Important APIs and types: `emi26_writememory()`, `emi26_set_reset()`, `emi26_load_firmware()`, `emi26_probe()`, and firmware declarations for `emi26/loader.fw`, `emi26/bitstream.fw`, and `emi26/firmware.fw`. It uses Intel HEX records, vendor requests `ANCHOR_LOAD_INTERNAL`, `ANCHOR_LOAD_EXTERNAL`, and `ANCHOR_LOAD_FPGA`, and EZ-USB `CPUCS_REG`.

Control flow: firmware load asserts CPU reset, writes the loader into internal RAM, releases reset, streams the FPGA bitstream in up-to-1023-byte chunks, reloads the loader, writes external firmware records while CPU runs, asserts reset, writes internal firmware records, releases reset, delays, and returns positive `1`. Probe ignores the return and returns `-EIO` by design.

State and persistence: no state survives probe; firmware is transiently requested and released. Device state is the loaded controller/FPGA RAM. Risks include legacy `usb_control_msg()` writes with short timeout, treating positive lengths as success without exact-length checks, a chunking loop that assumes non-null bitstream records, and intentionally failed probe confusing generic test expectations. Test signals include missing firmware diagnostics, USB control write traces, re-enumeration/real-driver bind behavior, and loader/FPGA/final firmware ordering.
