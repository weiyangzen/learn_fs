<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/acct.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/acct.h

## Purpose
Defines BSD-style process accounting record formats written by the kernel and consumed by accounting tools.

## Important APIs, Types, And Functions
Exports compact time/value types `comp_t` and `comp2_t`, record layouts `struct acct` and `struct acct_v3`, command length `ACCT_COMM`, accounting flags such as `AFORK`, `ASU`, `ACORE`, `AXSIG`, and byte-order/version constants.

## Control Flow
When process accounting is enabled, the kernel writes one record at task/process exit. Userspace accounting tools read records sequentially and decode flags, uid/gid, tty, start time, elapsed/user/system time, I/O, faults, swaps, exit code, and command name.

## State And Persistence
Records persist in the configured accounting file. The fields encode a point-in-time exit summary, not live process state. `struct acct` preserves older 16-bit uid/gid compatibility while `acct_v3` adds pid/ppid and full uid/gid fields.

## Dependencies And Integration Points
Depends on Linux integer types plus architecture `HZ`/byte order. Integrates with kernel accounting code, accton-style tools, and accounting log parsers.

## Risks And Edge Cases
Time range is limited by 32-bit start time, compact floating encodings lose precision, endianness must be honored, m68k padding differs under kernel build conditions, and userspace sees `acct_v3.ac_etime` as float while the kernel uses an integer representation.

## Test Signals
Validate binary record size/layout, endian byte-order flag, compact time decoding, v2/v3 parser compatibility, command truncation, and accounting records for normal exit, signal exit, core dump, and privileged execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/acct.h -->
