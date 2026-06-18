# sources/distributed-fs/ceph-client/sound/soc/spear/spdif_out_regs.h

Purpose: register map and bit definitions for the SPEAr S/PDIF output controller.

Important APIs/types: defines reset, FIFO, interrupt status/clear/enable, control, channel status, pause/latency, frame length, and config offsets. Control bits cover opmode, normal state, divider, and sample-read fields. Config bits select memory format, validity/user/channel-status/parity sources, and FIFO DMA trigger thresholds.

Control flow/state: no runtime state; values are consumed by `spdif_out.c`.

Dependencies/integration: private hardware header for the SPEAr output driver.

Risks/test signals: divider mask/shift and opmode constants are critical for clocking and mute behavior. Tests should validate register writes against hardware documentation and observed S/PDIF output framing.
