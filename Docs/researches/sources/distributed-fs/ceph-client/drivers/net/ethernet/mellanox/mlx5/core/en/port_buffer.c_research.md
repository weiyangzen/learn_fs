# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port_buffer.c

Purpose: implements DCB/PFC-aware manual port buffer configuration, including headroom sizes, xoff/xon thresholds, priority-to-buffer mapping, and shared-buffer pool allocation.

Important APIs/functions: `mlx5e_port_query_buffer` and `mlx5e_port_manual_buffer_config`. Internal helpers query shared-buffer pools, select SBCM pool parameters, update shared-buffer splits, set PBMC, calculate xoff, update lossless thresholds, and derive lossy/lossless buffer state from PFC.

Control flow: query reads PBMC, converts cell counts to bytes, and reports network, internal, spare, and headroom sizes. Manual config starts from current PBMC, computes xoff from link speed, cable length, and MTU, then applies requested change bits for cable length, PFC, prio-to-buffer, or explicit buffer sizes. Lossless buffers get xoff/xon thresholds and cannot be zero-sized; total requested headroom must fit current headroom plus spare. If needed, PBMC is written after shared-buffer pools and SBCM class settings are updated, then PPTB is written for prio mapping.

State and persistence: reads `priv->dcbx.port_buff_cell_sz`, `cable_len`, and `xoff`; updates `priv->dcbx.xoff` after successful/attempted recalculation. Firmware PBMC/SBPR/SBCM/PPTB writes persist port buffer configuration.

Dependencies and integration: uses `port.c` register wrappers, DCB PFC structures, pause/PFC queries, link speed, and mlx5 PCAM/SBCAM capabilities.

Risks: buffer-cell conversion truncates to firmware cell units. Shared-buffer pool update errors must happen before PBMC write to avoid inconsistent pool/buffer state. Threshold math requires enough size for xoff plus max MTU plus one cell.

Test signals: PFC on/off transitions, global pause handling, prio remapping, cable length changes, MTU extremes, insufficient buffer errors, and devices without SBCAM.
