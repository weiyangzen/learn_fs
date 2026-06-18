# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-vbi.c

## Purpose
`bttv-vbi.c` implements the V4L2 VBI capture queue and VBI format negotiation for bttv devices. It coordinates VBI line windows with video crop windows and builds VBI RISC programs through `bttv-risc.c`.

## Important APIs, Types, And Functions
The exported queue ops are `bttv_vbi_qops`, whose callbacks are `queue_setup_vbi()`, `buf_prepare_vbi()`, `buf_queue_vbi()`, `buf_cleanup_vbi()`, `start_streaming_vbi()`, and `stop_streaming_vbi()`. V4L2 ioctl helpers are `bttv_try_fmt_vbi_cap()`, `bttv_s_fmt_vbi_cap()`, `bttv_g_fmt_vbi_cap()`, and `bttv_vbi_fmt_reset()`. Internal `try_fmt()` clamps line starts/counts and fills VBI sampling metadata.

## Control Flow
VBI queue setup sizes buffers from `count[0] + count[1]` times `samples_per_line`. Prepare validates the plane size, marks field none, and calls `bttv_buffer_risc_vbi()`. Queueing starts VBI DMA when the VBI queue was empty, sharing `loop_irq` with active video streaming if needed. `start_streaming_vbi()` claims `RESOURCE_VBI`, resets IRQ state when video is not streaming, and returns queued buffers on conflict. Format setting rejects changes while VBI resources are held, clamps to the current TV norm and `crop_start`, updates `btv->vbi_fmt`, and records `end`, the earliest video line boundary.

## State And Persistence
VBI state is stored in `btv->vbiq`, `btv->vbi_fmt`, `btv->vbi_count[]`, `btv->vcapture`, and active `btv->cvbi`. `bttv_vbi_fmt_reset()` initializes default lines and maintains compatibility buffer size `VBI_BPL * VBI_DEFLINES * 2`. There is no disk persistence.

## Dependencies And Integration Points
This file depends on V4L2/videobuf2, bttv TV norm metadata (`vbistart`, `Fsc`, crop bounds), resource helpers in `bttv-driver.c`, RISC generation in `bttv-risc.c`, and IRQ completion in `bttv-driver.c`. The compatibility behavior is tied to older bttv userspace expectations.

## Risks
The code intentionally preserves legacy semantics where userspace may request overlapping VBI/video windows even though hardware aborts VBI at video start. Incorrect `crop_start`/`vbi_end` handling can allow VBI and video capture to compete for the same scan lines. The fixed `VBI_BPL` compatibility size can hide that the chip writes fewer samples per line. Queue conflict paths must return buffers in a state that vb2 userspace can recover from.

## Test Signals
Useful tests are `VIDIOC_TRY_FMT`/`S_FMT` VBI across PAL/NTSC norms, VBI read and streaming modes, VBI plus video concurrent capture with non-overlapping line windows, resource conflict returns, correct sequence stamping, and no timeout when only VBI streams.
