# sources/distributed-fs/ceph-client/include/linux/phonet.h

## Purpose
Kernel-side Phonet socket interface header. It bridges internal networking code with the UAPI Phonet definitions and declares private ioctl payloads for Phonet network interface autoconfiguration.

## Important APIs, Types, and Functions
Defines `SIOCPNGAUTOCONF` as a private device ioctl, `struct if_phonet_autoconf` with a one-byte `device` selector, and `struct if_phonet_req` with a fixed interface name and union payload. The `ifr_phonet_autoconf` macro aliases the union member.

## Control Flow
No executable control flow. Consumers populate these structures and pass them through network ioctl paths; Phonet handlers interpret the union based on ioctl command.

## State and Persistence
No owned state. The header describes transient ioctl state used to configure or query Phonet device assignment.

## Dependencies and Integration Points
Depends on `<uapi/linux/phonet.h>` for protocol constants and on network device ioctl infrastructure through `SIOCDEVPRIVATE`. Integrates with Phonet socket, netdevice, and userspace ioctl handling.

## Risks
Fixed-size interface naming and private ioctl layout require ABI discipline. Any field-size change would break user/kernel expectations. The `uint8_t device` field constrains device identifiers to the UAPI-defined Phonet range.

## Test Signals
Build tests for Phonet-enabled kernels, ioctl ABI tests, and runtime Phonet autoconfiguration tests should validate this header.
