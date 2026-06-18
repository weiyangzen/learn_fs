<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.c -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.c

Purpose: Implements the BRAM-buffer variant of the Xilinx HWICAP backend. It moves configuration/readback words between system memory and the ICAP core through a 2 KiB on-core storage buffer and polled control/status registers.

Important APIs/types/functions: Exports `buffer_icap_get_status()`, `buffer_icap_reset()`, `buffer_icap_set_configuration()`, and `buffer_icap_get_configuration()` for `struct hwicap_driver_config`. Helpers access BRAM words and registers: `buffer_icap_get_bram()`, `buffer_icap_set_bram()`, `buffer_icap_busy()`, `buffer_icap_set_size()`, `buffer_icap_set_offset()`, `buffer_icap_set_rnc()`, `buffer_icap_device_read()`, and `buffer_icap_device_write()`.

Control flow: writes copy input words into BRAM until the 512-word buffer fills, then program size/offset/direction, start configuration by writing RNC, and poll done with `XHI_MAX_RETRIES`; any transfer failure resets the core. Reads request chunks of up to 512 words from ICAP into BRAM, poll completion, then copy BRAM words to the caller. Status reads directly return the hardware status register; reset writes a magic value to the status register for internal core versions.

State and persistence: no private software state beyond hardware register and BRAM contents. The parent `hwicap_drvdata` serializes access and owns base address/device state.

Dependencies and integration: depends on big-endian MMIO accessors, `xilinx_hwicap.h` status masks/retry count, and the common `xilinx_hwicap.c` char-device read/write/open paths.

Risks: the transfer is fully polled with bounded retries, so slow hardware can produce `-EBUSY`. The buffer limit must be enforced on both offset and count. Comments for device read/write contain stale direction wording, so maintainers must trust register behavior rather than comments. Reset support differs across published core versions.

Test signals: on `xlnx,opb-hwicap-1.00.b`, write bitstream chunks larger and smaller than 2 KiB, perform register readback after a request packet, inject busy/timeout conditions if possible, verify DALIGN/status behavior, and test unaligned userspace byte writes through the parent driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.c -->
