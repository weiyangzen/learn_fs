<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.h

## Purpose

`option_ms.h` is the small internal header that exposes the Option ZeroCD initializer to unusual-device tables or usb-storage setup code.

## Important APIs, Types, and Functions

It has one include guard, `_OPTION_MS_H_`, and one declaration: `extern int option_ms_init(struct us_data *us);`. `struct us_data` is supplied by including context, normally `usb.h`.

## Control Flow

The header has no executable control flow. It allows code that selects device-specific init functions to call `option_ms_init()` without including the implementation file.

## State and Persistence Behavior

The header declares no state. Runtime state and device mode-switch behavior are entirely in `option_ms.c`.

## Dependencies and Integration Points

It integrates the Option mode-switch implementation with the usb-storage unusual-device mechanism. Include-order correctness matters because the prototype references `struct us_data`.

## Risks and Test Signals

Risk is limited to prototype drift. Build coverage should catch mismatches between this declaration and `option_ms.c`, missing `struct us_data` declarations, or incorrect include ordering in users of the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.h -->
