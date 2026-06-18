<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sh_fsi.h -->
# sources/distributed-fs/ceph-client/include/sound/sh_fsi.h

## Purpose
`sh_fsi.h` defines platform information for Renesas/SuperH Fifo-attached Serial Interface audio, especially SH7724-era boards.

## Important APIs, types, and functions
Flags include `SH_FSI_FMT_SPDIF`, `SH_FSI_ENABLE_STREAM_MODE`, and `SH_FSI_CLK_CPG`. `struct sh_fsi_port_info` stores flags and TX/RX IDs for one port. `struct sh_fsi_platform_info` groups port A and port B.

## Control flow
Platform code supplies per-port settings to the FSI driver. The driver uses flags to select S/PDIF, stream mode, and clocking behavior, and uses TX/RX IDs to bind DMA or hardware channels.

## State and persistence behavior
The header defines platform configuration only. Runtime stream state is handled by the driver.

## Dependencies and integration points
It includes clock and ASoC headers and connects board description to the Renesas FSI ASoC driver.

## Risks and test signals
Risks include wrong TX/RX ID mapping, incorrect clock-source flag, and S/PDIF flag mismatches for HDMI paths. Test signals include both ports, playback/capture DMA binding, 16-bit stream mode, S/PDIF output, and clock setup from CPG.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sh_fsi.h -->
