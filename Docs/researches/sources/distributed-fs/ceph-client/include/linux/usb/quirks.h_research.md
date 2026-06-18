# `sources/distributed-fs/ceph-client/include/linux/usb/quirks.h`

## Purpose

`quirks.h` defines device-wide USB quirk bits used by usbcore and drivers to compensate for non-compliant devices. Interface-specific quirks belong elsewhere; this header covers whole-device behavior.

## Important APIs, Types, and Constants

- Quirks cover string descriptor fetch size, reset-on-resume, no SetInterface, bad configuration/interface strings, no reset, honoring `bNumInterfaces`, delayed init, linear interrupt intervals, no device qualifier, ignoring remote wakeup, no LPM, disconnect before suspend, delayed control messages, slow hub reset, ignored endpoints, short SetAddress timeout, no BOS request, and force-one-configuration.

## Control Flow and Lifetimes

USB device ID tables or core matching set quirk bits during enumeration. usbcore checks these bits while reading descriptors, choosing configurations, setting interfaces, suspending/resuming, resetting ports, enabling LPM, and handling endpoint descriptors.

## State and Persistence Behavior

Quirk bits are runtime flags associated with a `usb_device` instance and persist until disconnect. The definitions are stable kernel ABI between quirk tables and usbcore behavior.

## Dependencies and Integration Points

It depends on `BIT()` from kernel bitops through including context. It integrates usbcore enumeration, hub, PM, descriptor parsing, and device-specific quirk tables.

## Risks and Edge Cases

Applying quirks too broadly can disable features for good devices. Missing quirks can break enumeration or resume. Some quirks change security- or power-relevant behavior such as ignoring remote wakeup or skipping BOS/LPM.

## Test Signals

Test devices listed in quirk tables, enumeration descriptor paths, resume/reset behavior, LPM enable/disable, SetInterface handling, slow hub reset, endpoint-ignore behavior, and regression tests ensuring unrelated devices are unaffected.
