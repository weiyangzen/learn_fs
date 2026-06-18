# sources/distributed-fs/ceph-client/drivers/hwmon/occ/p9_sbe.c

Purpose: POWER9/POWER10 OCC transport frontend using the SBE FIFO/FSI OCC interface. It also exposes SBE FFDC binary data after transport errors.

Important APIs/types/functions: `struct p9_sbe_occ` embeds `struct occ` and stores SBE parent device, FFDC buffer state, error flag, and lock. Key functions are `ffdc_read()`, `p9_sbe_occ_save_ffdc()`, transport callback `p9_sbe_occ_send_cmd()`, probe, and remove.

Control flow: `p9_sbe_occ_send_cmd()` calls `fsi_occ_submit()` up to three times for checksum errors (`-EBADE` with no FFDC), preserving original response length between attempts. If the transport returns FFDC data, it saves the first unread FFDC buffer and notifies the binary sysfs file. It then maps OCC return status to Linux errors. Probe initializes common OCC parameters, calls `occ_setup()`, maps `-ESHUTDOWN` to `-ENODEV`, and creates read-only `ffdc`.

State and persistence: FFDC data persists in memory until userspace reads through the buffer; once the read position reaches `ffdc_len`, `sbe_error` clears. Common OCC state stores sensors and hwmon lifecycle. `sbe` is nulled before shutdown on remove and FFDC memory is freed.

Dependencies and integration: depends on platform bus, parent FSI OCC device, `fsi_occ_submit()`, sysfs binary attributes, vmalloc helpers, and compatibles `ibm,p9-occ-hwmon` and `ibm,p10-occ-hwmon`. Probe sets 500 us power sample time and poll command data `0x20`.

Risks: only the first outstanding FFDC is preserved until read. FFDC allocation can fail and silently drop payload length. Common setup may be skipped when host is shut down. Return-status handling duplicates P8 mapping and must track OCC constants.

Test signals: successful P9/P10 FSI probe, checksum retry behavior, FFDC save/read/clear and sysfs notify, host-shutdown probe mapping, OCC status mappings, binary file cleanup, and common shutdown/free path.
