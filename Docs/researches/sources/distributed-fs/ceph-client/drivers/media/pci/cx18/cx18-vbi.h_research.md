# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-vbi.h

Declares the cx18 VBI processing interface: `cx18_process_vbi_data` for MDLs returned by firmware and `cx18_used_line` for VBI line filtering support elsewhere in the driver.

It integrates the queue layer, stream type checks, and AV subdevice VBI decoding. Callers are expected to pass complete VBI-frame buffers for the VBI stream type only.

Risks are mismatched stream type usage and missing definition/link coverage for declared helpers. Test signals are raw and sliced VBI captures and full-driver builds.
