# sources/distributed-fs/ceph-client/fs/smb/client/netmisc.c

## Purpose
`netmisc.c` provides low-level network address conversion and SMB/NT time conversion helpers. These routines are shared by mount parsing, network connection setup, directory metadata conversion, and SMB1/SMB2 timestamp handling.

## Important APIs, types, and functions
`cifs_convert_address()` parses IPv4 and IPv6 text into `struct sockaddr`, including numeric IPv6 scope IDs. `cifs_set_port()` sets the port on IPv4 or IPv6 socket addresses. `cifs_NTtimeToUnix()` converts little-endian NT time in 100ns units since 1601 to `struct timespec64`. `cifs_UnixTimeToNT()` converts Unix `timespec64` to NT time. `cnvrtDosUnixTm()` converts legacy DOS date/time fields plus server time adjustment into Unix time.

## Control flow
Address conversion first attempts IPv4 using `in4_pton()` with backslash as terminator, then IPv6 using `in6_pton()`. For IPv6 values containing `%`, it parses a decimal scope id with `kstrtouint()`. Time conversion subtracts or adds the NTFS epoch offset and uses `do_div()` carefully so negative NT times work on 32-bit builds. DOS conversion decodes bitfield date/time structures, logs invalid ranges, clamps invalid day/month, accounts for years since 1980, leap years, and the year-2100 exception, then applies the supplied offset.

## State and persistence behavior
The file holds no persistent state. It mutates caller-provided socket address buffers and returns computed timestamps.

## Dependencies and integration points
It depends on kernel inet parsers, byteorder helpers, `SMB_TIME`/`SMB_DATE` definitions, CIFS debug logging, and is used by metadata converters in `inode.c` and `readdir.c` for SMB1/DOS timestamp formats.

## Risks
Risks include parsing ambiguities for IPv6 scope IDs, accepting partial address strings due to delimiter behavior, arithmetic mistakes for pre-1970 NT times, invalid DOS date clamping hiding corrupt server data, leap-year edge cases around 2100, and port setting on uninitialized address families.

## Test signals
Test IPv4, IPv6, IPv6 scoped addresses, invalid scope strings, backslash-terminated UNC host components, unsupported families in `cifs_set_port()`, NT times before and after 1970, zero NT time, nanosecond precision truncation, DOS timestamps at leap-year boundaries, invalid day/month/hour/minute values, and server time-adjust offsets.
