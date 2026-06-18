
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusbdecfe.h

## Purpose
`ttusbdecfe.h` declares the private interface between the TTUSB DEC USB transport and its frontend wrappers.

## Important APIs, Types, and Functions
The key type is `struct ttusbdecfe_config`, containing a `send_command` callback with DVB frontend pointer, command byte, parameter buffer, result length, and result buffer. It declares `ttusbdecfe_dvbs_attach()` and `ttusbdecfe_dvbt_attach()`.

## Control Flow
The parent driver provides a config with a callback that routes frontend requests to the USB command protocol. The attach functions consume that config and return a DVB frontend for registration.

## State and Persistence
The header defines no state directly. The callback pointer is stored by the frontend state allocated in `ttusbdecfe.c`.

## Dependencies and Integration Points
It depends on Linux DVB frontend declarations and is included by both the USB driver and frontend implementation.

## Risks and Edge Cases
The callback is required for all meaningful frontend operations; a NULL or invalid callback would fail at runtime. The interface is synchronous and assumes the parent driver serializes USB command traffic.

## Test Signals
Compile-test both including files, verify attach symbols link, and test callback error propagation from parent USB command failures.
