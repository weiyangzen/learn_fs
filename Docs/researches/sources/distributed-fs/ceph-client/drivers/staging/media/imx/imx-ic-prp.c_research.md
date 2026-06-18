# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-prp.c

## Purpose
This file implements the i.MX IC preprocess router subdevice. It represents the PRP node that routes frames from CSI or VDIC into PRPENC and/or PRPVF downstream tasks, handles media-link constraints, propagates formats and frame intervals, chooses the IC source mux, and starts/stops upstream streaming.

## Important APIs and Functions
`struct prp_priv` stores pads, locks, source and downstream subdev pointers, validated CSI ID, a single mirrored media-bus format, frame interval, and stream count. `prp_start()` programs `ipu_set_ic_src_mux()` to select CSI or VDIC as the IC source. `prp_stop()` is currently empty.

Pad ops implement format enumeration, get/set format, get/set frame interval, and link validation. `prp_set_fmt()` bounds sink dimensions to 32..4096 with 16-pixel width alignment and 2-line height alignment, validates IPU YUV/RGB formats, and mirrors source pads to the sink format. `prp_link_setup()` enforces one upstream source, one PRPENC sink, one PRPVF sink, and disallows VDIC-to-PRPENC. `prp_link_validate()` runs default validation, finds the CSI subdevice when needed, enforces VDIC restrictions, and records CSI0/CSI1 ID.

`prp_s_stream()` validates links, only performs hardware/upstream start on transition from zero to one stream and stop on one to zero, then maintains `stream_count`. `prp_registered()` initializes default 1/30 frame interval and default mbus format. `prp_init()` allocates private state, initializes pads and mutex, and `imx_ic_prp_ops` exposes the operation table.

## Control Flow and State
Media graph setup populates `src_sd`, `sink_sd_prpenc`, and `sink_sd_prpvf`. Format state is stored as one active `format_mbus` mirrored to all pads. Link validation determines whether the source is VDIC or CSI and stores `csi_id`. Streaming sets the IPU IC source mux, calls upstream `s_stream`, and reference-counts multiple downstream users through `stream_count`.

No persistent disk state exists. Hardware state is limited to the IC source mux and upstream stream state.

## Dependencies and Integration Points
It depends on i.MX media helper APIs, V4L2 subdev/media entity operations, IPUv3 mux control, and group IDs for CSI/VDIC/PRPENC/PRPVF. It is registered via `imx_ic_prp_ops` from `imx-ic-common.c` and connects internal media graph entities.

## Risks and Test Signals
Risks include incorrect stream-count transition logic, link state races guarded only by the mutex, VDIC restrictions enforced at link setup/validation, default format propagation not modeling distinct downstream requirements, and `prp_stop()` doing no hardware cleanup beyond upstream stop. Test signals include media-ctl link enable/disable combinations, VDIC-to-PRPENC rejection, CSI ID validation for both CSI ports, format propagation, frame interval get/set, and streaming with one and two downstream consumers.
