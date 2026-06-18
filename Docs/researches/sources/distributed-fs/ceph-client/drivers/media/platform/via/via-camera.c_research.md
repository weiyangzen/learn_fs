# sources/distributed-fs/ceph-client/drivers/media/platform/via/via-camera.c

## Purpose
Implements the VIA Chrome integrated camera controller V4L2 capture driver, originally for OLPC XO-1.5 systems with an OV7670 sensor. The controller captures into reserved framebuffer memory, then copies completed frames into userspace-provided VB2 DMA-SG buffers.

## Important APIs, Types, And Functions
- Module parameters `flip_image` and `override_serial` tune OV7670 vertical flip and OLPC serial-port conflict handling.
- Core state is `struct via_camera`; queued buffers use `struct via_buffer`.
- Major paths cover GPIO sensor power/reset, OV7670 subdev configuration, VIA register access, threaded IRQ handling, framebuffer capture-buffer setup, scaler/controller configuration, VB2 queue ops, V4L2 file/ioctl ops, PM hooks, serial-port guard, probe, and remove.

## Control Flow
Probe validates framebuffer memory/MMIO, checks the OLPC serial-port conflict, allocates the camera object, registers V4L2 state, sets DMA mask, enables capture-port pins, powers the sensor, creates an OV7670 I2C subdev on `VIA_PORT_31`, requests a shared threaded IRQ, initializes a VB2 DMA-SG queue, and registers a video device. Open requests the VIA framebuffer DMA engine, powers the sensor, and marks configuration needed. Stream-on configures the sensor and controller when needed, adds a CPU latency QoS request, enables capture and interrupts, and starts filling internal framebuffer buffers. IRQ top-half clears camera interrupt bits and wakes the thread; the thread copies the just-completed framebuffer capture buffer into the next queued SG buffer, timestamps it, increments sequence, and completes it. Stop disables interrupts/capture, removes QoS, and returns queued buffers with error.

## State And Persistence
All state is in memory: current format, sensor format, mbus code, capture-buffer offsets, queue list, sequence, opstate, flags, GPIO handles, MMIO mappings, and QoS request. No durable persistence exists. The global `via_cam_info` assumes one device.

## Dependencies And Integration Points
Depends on VIA framebuffer core (`viafb_dev`, IRQ, DMA copy, I2C adapter lookup, PM hooks), V4L2 core/subdev/ctrl/event APIs, OV7670 sensor support, VB2 DMA-SG memory ops, GPIO descriptors, PCI config access for OLPC serial-port arbitration, and platform data from `viafb-camera`.

## Risks And Edge Cases
The driver is hardware- and board-specific: one capture engine, one global camera, fixed OV7670 address/port, VGA sensor mode, and OLPC-specific GPIO/pin assumptions. Frame data is copied from framebuffer memory in IRQ thread context, so bandwidth and SG correctness matter. Queue insertion lacks explicit locking in `buf_queue` beyond VB2 queue serialization. Suspend/resume must preserve prior running state and sensor power. Serial override intentionally disables a conflicting serial-port bit.

## Test Signals
Probe on XO-1.5/VIA Chrome9 with reserved camera framebuffer memory, verify `/dev/video*` registration, enumerate YUYV/QCIF-VGA formats, stream with mmap/userptr/dmabuf/read, test open/close power cycling, flip control, suspend/resume while idle and streaming, serial-port refusal/override, CPU latency QoS add/remove balance, no underruns with two/three internal capture buffers, and correct frame sequence/timestamps.
