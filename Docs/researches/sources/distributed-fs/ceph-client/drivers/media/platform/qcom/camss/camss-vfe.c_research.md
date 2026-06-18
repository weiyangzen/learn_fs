<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.c

## Purpose
Implements the shared VFE subdevice, format negotiation, power/clock management, entity registration, and generic v2 buffer flow for Qualcomm CAMSS. It is the central glue between SoC resource tables, hardware-specific VFE ops, media-controller subdevs, and the video capture nodes.

## Important APIs, Types, And Functions
- Exports format tables `vfe_formats_*`, lifecycle APIs `msm_vfe_subdev_init()`, `msm_vfe_register_entities()`, `msm_vfe_unregister_entities()`, `vfe_get()`, `vfe_put()`, `vfe_reset()`, `vfe_disable()`, `vfe_enable_v2()`, `vfe_queue_buffer_v2()`, `vfe_buf_done()`, `vfe_flush_buffers()`, WM reservation helpers, and ISR helpers.
- Implements V4L2 subdev core/video/pad ops for power, stream, mbus code/frame-size enumeration, get/set format, and PIX compose/crop selections.
- Owns supported RDI and PIX media-bus/pixel-format tables for old and newer SoCs.

## Control Flow
Initialization maps VFE and optional VBIF registers, attaches power domains, requests IRQs, acquires clocks and clock-rate tables, initializes locks/completions, and configures per-line format tables. Registration creates one V4L2 subdev and one video node per VFE line, then links each subdev source pad to its video sink. Power-on calls optional VFE power-domain ops, resumes runtime PM, computes clock rates from connected sensor pixel clocks, enables clocks, resets hardware, clears output maps, initializes output state, and logs hardware version. Stream-on sets the line output reserved and dispatches to hardware `vfe_enable`; stream-off dispatches to hardware `vfe_disable`. The v2 path uses one WM per line, primes up to two buffers, updates addresses, and completes buffers in `vfe_buf_done()`.

## State And Persistence
State is in `struct vfe_device` and `struct vfe_line`: power and stream reference counts, clock arrays, power-domain links, WM-to-line maps, output state, pending buffers, active buffer slots, completions, and active pad formats/selections. No durable persistence exists. `power_lock`, `stream_lock`, and `output_lock` guard concurrent state transitions.

## Dependencies And Integration Points
Depends on Linux clocks, PM runtime, generic PM domains, platform resources, IRQs, media-controller/V4L2 subdev APIs, VB2, and helper functions from `camss.c` for sensor lookup, pixel clocks, clock margin, and CSID register updates. Hardware-specific ops come from Gen1, Titan/IFE, and Gen3 VFE implementations selected by SoC resources.

## Risks And Edge Cases
Clock-rate selection depends on sensor `V4L2_CID_PIXEL_RATE`; absent controls force fallback behavior and can mask underclocking. Format and crop constraints differ for RDI and PIX; invalid propagation can lead to `-EPIPE` at video start. Power-count or stream-count imbalance can leave clocks/domains on or trigger errors. The generic v2 output mapping notes that line-to-WM identity will not work for PIX streams. Register-reset and halt paths are timeout-sensitive.

## Test Signals
Probe/register/unregister should succeed for each compatible resource table. Media graph inspection should show CSID/ISPIF/VFE/video links. V4L2 compliance should cover mbus code enumeration, selection bounds, format propagation, stream-on/off, buffer completion, power cycling, and runtime PM/interconnect behavior across RDI and PIX lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.c -->
