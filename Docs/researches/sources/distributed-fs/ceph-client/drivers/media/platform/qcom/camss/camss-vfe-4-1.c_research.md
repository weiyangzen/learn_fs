
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-1.c

## Purpose
Implements first-generation VFE 4.1 ops for MSM8916-style CAMSS. It supports RDI and PIX paths, CAMIF programming, demux/scale/crop/clamp blocks, bus write masters, UB allocation, IRQ dispatch, halt/reset, and optional PM domains.

## Important APIs, Types, and Functions
Exports `vfe_ops_4_1` and the gen1 vtable `vfe_ops_gen1_4_1`. Key helpers include WM enable/frame/line programming, ping/pong address setup, UB config, bus RDI connect/disconnect, xbar config, RDI CID selection, reg update, per-line/common IRQ enables, CAMIF config/cmd/stop polling, module config, QoS/VBIF setup, and ISR read/dispatch.

## Control Flow
Generic gen1 enable code calls this file through `vfe->ops_gen1`. RDI paths connect a WM to the selected RDI, configure frame-based bus writes and UB, then issue register updates. PIX paths configure demux, scaler, crop, clamp, CAMIF dimensions and pixel order, xbar streams, composite masks, and CAMIF frame-boundary commands. The ISR reads/clears status, dispatches reset ack, violations, halt ack, line reg updates, SOF, composite done, and WM ping-pong completions.

## State and Persistence
Uses common `vfe_device` state: output locks, per-line `vfe_output`, `reg_update`, WM maps, power/stream counts, and completions. Registers are volatile; no disk persistence.

## Dependencies and Integration Points
Integrates with `camss-vfe-gen1.c`, VBIF settings, PM-domain helpers, V4L2 formats, media graph VFE lines, and buffer queues.

## Risks and Test Signals
VFE 4.1 only returns UB size for VFE id 0; dual-VFE assumptions must be resource-matched. Pixel path math assumes YUV widths and subsampling. Test RDI and PIX streaming, CAMIF halt timeout, VBIF failures, IRQ masks, UB partitioning, scaler/crop output, and PM-domain conditional paths.
