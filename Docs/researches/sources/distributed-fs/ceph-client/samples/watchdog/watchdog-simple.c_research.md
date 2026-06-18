# sources/distributed-fs/ceph-client/samples/watchdog/watchdog-simple.c

## Purpose
`watchdog-simple.c` is a minimal userspace program that opens `/dev/watchdog` and periodically writes a byte to keep the watchdog from firing.

## APIs, Types, And Functions
The single `main()` uses `open()`, `write()`, `sleep()`, `close()`, `perror()`, and standard exit codes. It opens the watchdog device write-only.

## Control Flow
After opening `/dev/watchdog`, the program loops forever writing one NUL byte and sleeping ten seconds. If a write returns anything other than one byte, it breaks, closes the fd, and returns `-1`.

## State And Persistence
State is the watchdog fd and last write result. Opening and writing may arm or pet a hardware/software watchdog; device behavior may persist outside the process depending on driver configuration.

## Dependencies And Integration Points
It depends on a watchdog device node and watchdog driver semantics. It integrates with the Linux watchdog character device ABI.

## Risks And Test Signals
Running it on real hardware may keep or arm a system reset watchdog, and abrupt exit behavior depends on the driver magic-close policy. Test signals include successful open, regular writes visible via tracing, and expected error if `/dev/watchdog` is absent or permission denied.
