# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-sram.h

Purpose: defines fixed cx25821 SRAM layout for command blocks, instruction queues, cluster descriptor tables, and FIFO cluster buffers used by video, audio, and Mobilygen interface DMA channels.

Important APIs and constants: sizing constants include `VID_CMDS_SIZE`, `AUDIO_CMDS_SIZE`, `VID_IQ_SIZE`, `AUDIO_IQ_SIZE`, `VID_CDT_SIZE`, `AUDIO_CDT_SIZE`, `VID_CLUSTER_SIZE` 1440, and `AUDIO_CLUSTER_SIZE` 128. Address constants map RX and TX SRAM regions such as `VID_A_DOWN_CMDS`, `VID_A_IQ`, `VID_A_CDT`, `VID_A_DOWN_CLUSTER_1`, upstream video clusters, and audio clusters. Conversion helpers include `BYTES_TO_DWORDS`, `BYTES_TO_QWORDS`, and `BYTES_TO_OWORDS`.

Control flow: `cx25821-core.c` uses these addresses to populate `cx25821_sram_channels[]`; SRAM setup writes command, CDT, FIFO, pointer, and count registers based on each channel descriptor. Video and audio DMA then point hardware at these SRAM regions.

State and persistence: no software state. Constants describe hardware SRAM address allocation; actual SRAM contents are initialized during device setup and DMA start.

Dependencies and integration points: included by `cx25821.h` and `cx25821-core.c`. It must remain consistent with `struct sram_channel` descriptors and `cx25821-reg.h` DMA register constants.

Risks: static layout leaves little room for runtime validation; overlapping or incorrect addresses would cause cross-channel DMA corruption. Comments show several legacy/reserved regions, so maintainers must avoid assuming all apparent free space is usable. Audio channel setup expects only three audio clusters, unlike video's four.

Test signals: SRAM channel dump output, successful concurrent multi-channel video capture, audio capture, and RISC error diagnostics showing expected command/CDT/FIFO ranges.
