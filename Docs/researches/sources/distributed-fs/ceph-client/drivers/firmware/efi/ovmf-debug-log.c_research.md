
# sources/distributed-fs/ceph-client/drivers/firmware/efi/ovmf-debug-log.c

Purpose: maps an OVMF debug log buffer advertised through EFI and exposes it as `/sys/firmware/efi/ovmf_debug_log`.

Important APIs/types/functions: exports `ovmf_log_probe()`. Internal `struct ovmf_debug_log_header` describes ring-buffer metadata and `ovmf_log_read()` implements binary sysfs reads.

Control flow: probe maps the header, validates two magic values, logs firmware version and buffer size, remaps the full header+log buffer, sets `logbuf` and `logbufsize`, sets sysfs bin attribute size, and registers the binary file. Reads compute ring-buffer start/end from head/tail offsets, handle wraparound, clamp to log and tail bounds, and copy available bytes.

State and persistence behavior: static `hdr`, `logbuf`, and `logbufsize` hold the mapped firmware buffer for the kernel lifetime unless probe fails and unmaps. The sysfs file exposes live firmware log memory.

Dependencies and integration points: depends on EFI table discovery by caller, memremap, EFI kobject, and sysfs binary attributes. Intended for OVMF/EDK2 debug firmware.

Risks and test signals: header fields are trusted after magic validation; bad offsets can make reads return zero or expose truncated data. Attribute size is header+log size while read addresses log bytes, so offsets need careful user expectations. Test signals include valid/invalid magic, wrapped and non-wrapped buffers, truncated flag scenarios, sysfs registration failure, and bounds checks.
