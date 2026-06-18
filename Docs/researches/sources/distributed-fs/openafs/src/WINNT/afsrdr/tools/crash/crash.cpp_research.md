# sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/crash/crash.cpp

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/crash/crash.cpp` is a diagnostic utility that asks the OpenAFS redirector to intentionally crash through `IOCTL_AFS_FORCE_CRASH`. The complete 84-line file was read.

## Important APIs, Types, and Functions

The only executable function is `main`. It opens `AFS_SYMLINK` with `CreateFile`, sends `DeviceIoControl(IOCTL_AFS_FORCE_CRASH)`, closes the handle, and exits. It includes `AFSUserDefines.h` and `AFSUserIoctl.h` for the control device path and IOCTL code.

## Control Flow

There is no argument parsing. Failure to open the control device prints `GetLastError()` and returns `0`; otherwise the crash IOCTL is issued once and the device handle is closed.

## State and Persistence Behavior

The tool has no local persistence. Its intended effect is a system-level driver crash or bugcheck path controlled by the redirector implementation, so any persistence is crash dump and system log output produced outside this program.

## Dependencies and Integration Points

The integration point is the redirector control device behind `AFS_SYMLINK`. Dispatch for the crash IOCTL is visible in `kernel/fs/AFSCommSupport.cpp`.

## Risks and Edge Cases

This utility is intentionally destructive and should not be installed or run casually. It ignores the `DeviceIoControl` return value, so a failed crash request is silent. Returning `0` even on open failure makes automation treat failure as success unless it parses stdout.

## Test Signals

Validation should be limited to controlled debug or test systems. Expected signals are successful control-device open, crash dump generation or driver verifier output, and correct access control preventing unprivileged accidental use if the driver enforces it.
