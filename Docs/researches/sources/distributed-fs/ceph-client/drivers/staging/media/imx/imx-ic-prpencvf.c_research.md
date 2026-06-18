# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-prpencvf.c

## Purpose
This file implements the i.MX IC PRP encoder/viewfinder capture subdevice. It takes frames from the PRP router, performs IC resize/colorspace conversion and optional rotation/flips through IPUv3 channels, feeds a capture video device, manages vb2 buffer completion, handles EOF/error interrupts, and exposes pad formats, frame sizes, frame intervals, media links, and rotation controls.

## Important APIs and Functions
`struct prp_priv` stores IC/IPU resources, output/rotation channels, active capture buffers, underrun and rotation DMA buffers, media sink/source state, per-pad mbus formats and pixel formats, controls, rotation mode, IRQ/timer state, stream count, sequence, and error flags.

Resource helpers `prp_get_ipu_resources()` and `prp_put_ipu_resources()` acquire/release the IC task and output/rotation IDMAC channels based on encoder or viewfinder task. Buffer helpers `prp_setup_vb2_buf()`, `prp_unsetup_vb2_buf()`, and `prp_vb2_buf_done()` manage the two active IPU buffers, queued capture buffers, underrun buffer fallback, timestamps, sequence, and error completion on NFB4EOF.

Interrupt handlers are `prp_eof_interrupt()` and `prp_nfb4eof_interrupt()`. EOF completes or advances capture buffers, toggles the IPU double-buffer index, and refreshes an EOF timeout timer. NFB4EOF marks the next frame as error. `prp_eof_timeout()` reports fatal capture-device error.

Pipeline setup functions include `prp_setup_channel()`, `prp_setup_rotation()`, `prp_unsetup_rotation()`, `prp_setup_norotation()`, `prp_unsetup_norotation()`, and `prp_unsetup()`. They calculate CSC, configure CPMEM image layout/burst/rotation/interweave/odd chroma skipping, initialize IC tasks, allocate rotation buffers when needed, link rotation channels, enable IC/IDMAC channels, and select double buffers.

`prp_start()` acquires resources, allocates underrun buffer, initializes counters/completions, configures rotation or non-rotation pipeline, requests EOF and NFB4EOF IRQs, starts upstream streaming, and starts the timeout timer. `prp_stop()` marks last EOF, waits for completion or timeout, stops upstream, frees IRQs, unsets hardware, returns active buffers as error, frees DMA buffers, deletes timer, and releases IPU resources.

Pad/control/media ops implement format enumeration, get/set/try formats, frame size enumeration, link setup, `s_stream`, frame interval get/set, registration/unregistration, and controls. `prp_bound_align_output()` enforces IC downscale and rotation alignment constraints. `prp_s_ctrl()` derives `rot_mode` from rotation/hflip/vflip and rejects changes that would alter active output bounds or occur while streaming. `prp_registered()` initializes formats, capture video device, and controls.

## Control Flow and State
Media graph setup links one upstream subdev to one capture video device. Active formats are stored per pad; sink changes propagate a default source format. Controls derive `rot_mode`, which decides whether the hardware path is direct IC-to-memory or IC-to-memory plus memory-to-IC-rotation plus rotation-to-memory. Streamon validates source/sink, performs setup only on zero-to-one transition, starts upstream after hardware is ready, then EOF IRQs drive frame completion. Streamoff waits for a final EOF before tearing down to avoid disabling active channels mid-frame.

Persistent state is in `prp_priv` while the subdevice exists: format/cc arrays, capture vdev, control values, resource pointers, active buffers, IRQ numbers, timer, stream count, sequence, and flags. DMA buffers are allocated per stream and freed at stop.

## Dependencies and Integration Points
It depends on V4L2 subdev/control/media APIs, i.MX media capture helpers, vb2 DMA-contig addresses, IPUv3 IC/IDMAC/CPMEM/rotation APIs, timer and IRQ infrastructure, and the common IC wrapper. Encoder and viewfinder tasks use different IPU channel IDs from the `prp_channel` table.

## Risks and Test Signals
Risks include complex teardown ordering around IRQs/timers/channels, underrun-buffer use hiding missing capture buffers, EOF timeout as fatal condition, interlaced/interweave stride handling, rotation-buffer allocation failures, stream-count transitions, refusing rotation changes when output alignment would change, and returning active buffers with error on normal stop. Test signals include capture without rotation, capture with 90/180/270 and h/v flips, planar YUV and interlaced formats, missing queued-buffer underrun behavior, EOF/NFB4EOF IRQ handling, timeout recovery, streamon/off stress, media link validation, frame size bounds, and `v4l2-compliance` on the generated capture node.
