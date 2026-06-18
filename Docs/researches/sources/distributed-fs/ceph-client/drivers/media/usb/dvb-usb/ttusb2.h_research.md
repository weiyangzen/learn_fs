# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/ttusb2.h

## Purpose
This header documents the TTUSB2 64-byte command protocol and names command byte constants used by `ttusb2.c`.

## Important APIs, types, and functions
It defines commands for DSP download/boot, power, LNB, version reads, DiSEqC, PID/filter operations, DSP version, I2C transfer, and I2C bitrate. The protocol comment defines the outgoing `0xaa id cmd len data` and incoming `0x55 id cmd len data` framing.

## Control flow and state
There is no runtime state. The constants drive `ttusb2_msg()` request construction and response validation in the C file.

## Dependencies and integration
The header is included only after `dvb-usb.h` in `ttusb2.c` and is tightly coupled to the firmware command ABI.

## Risks and test signals
Risk is command ABI mismatch with firmware. Test by issuing power, I2C, version, RC, and CI commands on supported devices and confirming response headers and lengths match the header's documented frame.
