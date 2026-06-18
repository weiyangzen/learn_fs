# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_v4l2.h

## Purpose

`uvc_v4l2.h` declares the V4L2 operation tables implemented by `uvc_v4l2.c` for the UVC gadget video node.

## Important APIs, Types, and Functions

It exports `uvc_v4l2_ioctl_ops` and `uvc_v4l2_fops`. The ioctl table is consumed when registering the `video_device`; the file-operations table handles open, release, ioctl dispatch, mmap, poll, and optional no-MMU support.

## Control Flow

There is no runtime logic in the header. UVC function setup code assigns these tables into the V4L2 video device so all userspace interactions enter `uvc_v4l2.c`.

## State and Persistence Behavior

The header defines no state. It declares immutable operation-table symbols.

## Dependencies and Integration Points

It depends on V4L2 type declarations being visible at the use site and integrates UVC gadget registration code with the V4L2 implementation.

## Risks and Test Signals

Risks are limited to symbol mismatch or missing includes after refactors. Build coverage of the UVC function and successful video-device registration are the main signals.
