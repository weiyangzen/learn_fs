# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-vbi.c

Post-processes CX23418 VBI buffers returned by firmware. It byte-swaps firmware data, compresses raw VBI, decodes sliced VBI through the AV subdevice, and optionally builds MPEG private-stream VBI payloads.

Important functions are `cx18_process_vbi_data`, `_cx18_process_vbi_data`, `compress_raw_buf`, `compress_sliced_buf`, and `copy_vbi_data`. Raw mode strips SAV bytes and appends a frame counter. Sliced mode scans for EAV codes, calls `decode_vbi_line`, writes `v4l2_sliced_vbi_data` into the buffer, maintains at least one empty line, and may package PTS-tagged MPEG data.

State is in `cx->vbi`: frame counters, decoded line buffers, MPEG insertion buffers, and size tables. Risks include the raw compression FIXME that ignores input size, endian assumptions, and the assumption that each buffer contains a complete VBI frame. Test signals are raw/sliced capture, CC/teletext decoding, MPEG insertion, and malformed/short VBI buffers.
