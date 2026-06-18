<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/adb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/adb.h

## Purpose
Defines Apple Desktop Bus command and packet constants used by old Macintosh ADB controller/userspace interfaces.

## Important APIs, Types, And Functions
Macros build ADB command bytes: `ADB_BUSRESET`, `ADB_FLUSH`, `ADB_WRITEREG`, and `ADB_READREG`. It defines default device ids, return codes, packet kinds for ADB/CUDA/PMU/etc., and `ADB_QUERY_GETDEVINFO`.

## Control Flow
Consumers encode command bytes with device id/register fields, submit them to the ADB controller interface, and interpret returned packet or query data according to packet type and return status.

## State And Persistence
The header has no persistent storage; device addressing and handler ids are bus/controller state. Bus reset and flush affect live device/controller state.

## Dependencies And Integration Points
Integrates with legacy ADB, CUDA, PMU, timer, power, and Mac IIC packet providers in old Apple hardware support.

## Risks And Edge Cases
Command byte bit packing is easy to misuse, device ids are defaults rather than guaranteed live addresses, and controller-specific packet emulation may not support all packet classes.

## Test Signals
Compile tests plus hardware/emulator tests for reset, read/write register, flush, timeout handling, and get-device-info query responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/adb.h -->
