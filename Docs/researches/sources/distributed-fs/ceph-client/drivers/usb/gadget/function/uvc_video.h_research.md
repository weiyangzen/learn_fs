# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_video.h

## Purpose

`uvc_video.h` declares the UVC gadget video streaming lifecycle functions used outside `uvc_video.c`.

## Important APIs, Types, and Functions

The header forward-declares `struct uvc_video` and exports `uvcg_video_enable()`, `uvcg_video_disable()`, and `uvcg_video_init()`. These are the control surface for V4L2 stream operations and UVC function setup.

## Control Flow

UVC device initialization calls `uvcg_video_init()`. V4L2 STREAMON calls `uvcg_video_enable()`, and STREAMOFF, release, unsubscribe, or disconnect paths call `uvcg_video_disable()`.

## State and Persistence Behavior

The header stores no state; it declares functions that mutate `struct uvc_video` runtime state.

## Dependencies and Integration Points

It is included by V4L2, queue, and UVC function code that needs to manage video streaming without depending on private implementation details.

## Risks and Test Signals

Risks are limited to API drift between callers and implementation. Build coverage and successful stream lifecycle tests validate it.
