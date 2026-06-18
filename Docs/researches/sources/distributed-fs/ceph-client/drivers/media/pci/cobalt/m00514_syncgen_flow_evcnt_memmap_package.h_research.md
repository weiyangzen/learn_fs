<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00514_syncgen_flow_evcnt_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00514_syncgen_flow_evcnt_memmap_package.h

Purpose: Register map for the HSMA video output sync generator, flow-control, and event counter block.

Important APIs/types: `struct m00514_syncgen_flow_evcnt_regmap` maps output control, horizontal/vertical sync/backporch/active/frontporch lengths, error color, read status, and event count. Masks cover parameter load, sync generator enable, output enable, sync polarity, event counter enable/clear, 16-bpp format, error color channels, no-data, and ready-buffer-full status.

Control flow: `cobalt_enable_output()` writes timing parameters from V4L2 DV timings, sets error color, loads parameters, clears counters, and enables sync generation plus flow-control output. DMA start/stop clear/enable/disable the event counter.

State/persistence: Hardware output timing and status persist while output is configured. Stream format/timings are the software source.

Dependencies/integration: Used by Cobalt V4L2 output path through `COBALT_TX_BASE()`, with CPLD clock programming and ADV7511 output subdevice setup.

Risks: Timing registers must match the programmed output pixelclock; mismatches can break HDMI output. Format bit only distinguishes 16 bpp versus other formats, so caller must keep it in sync with packer/subdevice format.

Test signals: HDMI output at 1080p60 and other timings, no-data/ready-buffer-full status, event count increment, YUYV versus BGR32 output, and monitor lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00514_syncgen_flow_evcnt_memmap_package.h -->
