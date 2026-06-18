# sources/distributed-fs/ceph-client/include/linux/joystick.h

## Purpose
Provides the in-kernel wrapper for the joystick UAPI header and selects the architecture-sized `JS_DATA_SAVE_TYPE` constant.

## Important APIs, Types, And Functions
The header includes `uapi/linux/joystick.h` and defines `JS_DATA_SAVE_TYPE` as `JS_DATA_SAVE_TYPE_64` on 64-bit builds or `JS_DATA_SAVE_TYPE_32` on 32-bit builds. Unsupported word sizes trigger a preprocessor error.

## Control Flow
There is no runtime control flow. The preprocessor selects the ABI save type based on `BITS_PER_LONG` at compile time.

## State And Persistence
No state is stored. The resulting macro affects how joystick driver code interprets or saves data layout.

## Dependencies And Integration Points
Depends on the joystick UAPI definitions and architecture word-size definitions. It integrates with input joystick drivers and compatibility paths that need stable data layout.

## Risks
Incorrect `BITS_PER_LONG` configuration would select the wrong ABI layout. New or unusual architectures with unsupported word sizes fail compilation, which is safer than silently choosing an invalid layout.

## Test Signals
Build coverage on 32-bit and 64-bit targets is the primary signal. Runtime joystick ioctl tests should confirm event and calibration data remain compatible with the UAPI layout.
