# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpaa2-console.c

Purpose: DPAA2 firmware console driver. It exposes Management Complex and AIOP circular firmware log buffers as misc character devices `/dev/dpaa2_mc_console` and `/dev/dpaa2_aiop_console`.

Important APIs and functions: `dpaa2_console_probe()` records the MC firmware base-address register resource and registers both misc devices. `get_mc_fw_base_address()` maps MC base registers and reconstructs the firmware base address. `dpaa2_generic_console_open()` maps a log buffer, validates magic, computes start/end/current pointers, and handles wraparound. `dpaa2_console_read()` copies log bytes from IO memory to userspace, including circular wrap handling. `dpaa2_console_remove()` deregisters devices.

Control flow: probe only prepares global resource and device nodes. Each open maps the firmware log buffer based on current MC base address, verifies header fields, and initializes per-file `console_data`. Reads refresh `last_byte`, limit to requested count, copy in one or two segments, and advance `cur_ptr`; close unmaps and frees.

State and persistence: global `mc_base_addr` stores the base register resource. Per-open `console_data` stores MMIO mapping and read cursor, so each file descriptor has independent read position. Firmware log memory is external persistent state owned by MC/AIOP firmware.

Dependencies and integration: depends on OF resource translation, miscdevice, IO mapping, firmware log header layout, and userspace reads through char devices.

Risks and test signals: risks include trusting firmware-provided `buf_start`/`buf_length`, large per-read `kmalloc(count)`, races with firmware updating circular buffer, and mapping failure when MC base registers are unavailable. Test signals are correct misc devices, magic validation, wraparound reads, EOF behavior when `cur_ptr == end_of_data`, and clean unload/reprobe.
