<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sur40.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/sur40.c

## Purpose
`sur40.c` drives the Microsoft/Samsung SUR40 PixelSense USB device. It exposes two interfaces from one USB driver: a polled multitouch input device for blob/contact data and a V4L2 touch/video capture device for raw sensor frames, with controls for brightness, contrast, gain, and backlight/preprocessor behavior.

## Important APIs, Types, And Functions
The wire formats are `struct sur40_header`, `struct sur40_blob`, and `struct sur40_image_header`. `struct sur40_state` owns the USB device, input device, V4L2 device/video_device, vb2 queue, buffer list/spinlock, pixel format, controls, bulk input buffer, endpoint metadata, and device path. `sur40_command()`/`sur40_poke()` perform vendor control transfers. `sur40_report_blob()` converts blob geometry to input MT fields. `sur40_poll()` reads touch bulk packets from endpoint `0x86`, reports all blobs, then calls `sur40_process_video()` if V4L2 streaming is active. The vb2 and V4L2 operations implement buffer setup, streaming, format enumeration, and ioctls.

## Control Flow
Probe matches USB VID/PID, validates interface class/endpoints, allocates state and input, configures 64 MT slots, sets up input polling at 1 ms, allocates a bulk buffer, registers the input device, registers V4L2, initializes a DMA-SG vb2 queue, creates controls, and registers the video device. Input open initializes the SUR40 and enables polling; close marks V4L2 sequence stopped. Polling reads one or more touch packets until the blob count is satisfied, then optionally reads a video header plus a scatter-gather frame into the next queued vb2 buffer.

## State And Persistence
Runtime state includes control values, current V4L2 pixel format, buffer queue, sequence counter, and device `vsvideo` register byte. Module parameters set initial brightness/contrast/gain. Control writes are sent to device registers but not permanently written; comments warn against the permanent-write index because it previously corrupted EEPROM.

## Dependencies And Integration Points
It integrates with USB bulk/control APIs, input polling and MT, V4L2 device/control/ioctl frameworks, videobuf2 DMA-SG memory, spinlocks/mutexes, and module parameters. It registers as a USB driver for Microsoft `045e:0775`.

## Risks
The driver mixes input polling with video frame acquisition: video frames are pulled only when input polling runs. Bulk endpoint assumptions are strict (`endpoint[4]` must be `0x86`). SUR40 vendor commands are sensitive; the code documents EEPROM corruption risk from wrong control recipient/index. Video buffer error paths must always return queued buffers; streaming stop uses `sequence = -1`. Touch packet packet-id checks are intentionally disabled because video acquisition can disturb IDs.

## Test Signals
Validate probe on the correct interface, evtest/libinput with many blob contacts, V4L2 capability/format/frame interval enumeration, `mmap`/read/DMABUF streaming, control writes for brightness/contrast/gain/backlight, buffer underrun behavior, disconnect cleanup, and absence of EEPROM-permanent writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sur40.c -->
