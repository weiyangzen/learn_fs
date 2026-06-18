# sources/distributed-fs/ceph-client/drivers/media/platform/intel/pxa_camera.c

## Purpose
This file implements the V4L2 capture driver for the PXA27x Quick Capture Interface. It binds a single external camera sensor through V4L2 async subdevice discovery, configures the PXA camera interface registers, manages vb2 DMA-SG capture buffers, and delivers captured frames through a `/dev/video*` node.

## Important APIs, Types, And Functions
Important register macros cover CICR/CISR/CIFR/CITOR/CIBR registers and their control bits. Format modeling is handled by `struct pxa_mbus_pixelfmt`, `struct pxa_mbus_lookup`, and `struct pxa_camera_format_xlate`. Runtime state is held in `struct pxa_camera_dev`, which contains V4L2/vb2/notifier objects, the sensor subdev, DMA channels, locks, current format, register save state, and queued/active buffers. `struct pxa_buffer` embeds `vb2_v4l2_buffer` and stores DMA descriptors, cookies, scatterlists, plane sizes, and active-DMA bit state.

Key functions include `pxa_mbus_build_fmts_xlate()`, `pxa_camera_set_bus_param()`, `pxa_camera_setup_cicr()`, `pxa_buffer_init()`, vb2 callbacks `pxac_vb2_*`, DMA helpers `pxa_dma_add_tail_buf()`, `pxa_dma_start_channels()`, and `pxa_camera_dma_irq()`, V4L2 ioctl handlers `pxac_vidioc_*`, async sensor callbacks `pxa_camera_sensor_bound()` / `pxa_camera_sensor_unbind()`, PM hooks, DT parsing, and `pxa_camera_probe()` / `pxa_camera_remove()`.

## Control Flow
Probe allocates `pxa_camera_dev`, maps registers, registers a V4L2 device, gathers platform data or DT endpoint data, requests three DMA channels (`CI_Y`, `CI_U`, `CI_V`), configures DMA source addresses, activates the camera clock/register defaults, requests the QCI IRQ, and registers a V4L2 async notifier. When the sensor binds, the driver builds host/sensor format translations, sets a default 640x480 format, powers and configures the sensor, initializes vb2, and registers the video device.

Format setting validates hardware frame bounds, negotiates subdev media-bus format, computes bytesperline and image size, stores `current_fmt/current_pix`, and programs CICR registers. Streaming queues vb2 buffers, splits the single user plane into Y/U/V DMA scatterlists for planar mode, submits reusable DMA descriptors, and starts capture. EOF from the camera interrupt disables further EOF interrupts and schedules bottom-half work, which resets FIFOs, chooses the first queued buffer, marks active DMA channels, and issues pending DMA. DMA callbacks clear the completed channel bit; once all active planes for a buffer complete, `pxa_camera_wakeup()` timestamps, sequences, completes the vb2 buffer, and advances to the next queued buffer. FIFO overruns trigger capture stop, descriptor resubmission, and restart.

## State And Persistence
Persistent runtime state is in `pcdev`: current format, bus flags, clock rates, DMA channels, capture list, `active` buffer pointer, `buf_sequence`, and saved CICR registers for suspend/resume. No state is persisted beyond device lifetime. The driver saves CICR0-4 over suspend, powers the sensor down/up, and restarts capture if an active buffer existed.

## Dependencies And Integration Points
The driver depends on V4L2 core, V4L2 async/fwnode, vb2 DMA-SG, DMAengine, PXA DMA slave IDs, platform data in `linux/platform_data/media/camera-pxa.h`, OF graph endpoints, and camera subdevices implementing pad operations and optional `s_power` / `g_skip_top_lines`. It integrates with kernel PM through `dev_pm_ops`, with the media userspace ABI through standard video capture ioctls, and with optional `CONFIG_VIDEO_ADV_DEBUG` register access ioctls.

## Risks
The most sensitive code is the DMA hot-chaining path. The driver submits descriptors while DMA can already be running and compensates for missed links with `pxa_camera_check_link_miss()`. FIFO overrun recovery restarts the whole capture path and must not lose queued buffers. Format handling assumes one vb2 plane even for YUV422P and splits that memory into hardware planes; bad size calculations can corrupt memory or produce invalid planar layout. Locking spans spinlocks in IRQ/DMA contexts and a mutex for file/vb2 operations, so active-buffer races are a regression risk. The probe path initializes vb2 both before and after sensor bind, which should be watched when refactoring.

## Test Signals
Build with `CONFIG_VIDEO_PXA27x` and `COMPILE_TEST`. Runtime tests should cover sensor async bind/unbind, format enumeration and set/try for packed and planar formats, streaming with one and multiple buffers, FIFO overrun recovery, DMA callback completion for 1-plane and 3-channel modes, streamoff returning queued buffers as errors, suspend/resume during idle and active capture, and DT endpoint parsing for bus width and polarities. V4L2 compliance and media pipeline tests are important external signals.
