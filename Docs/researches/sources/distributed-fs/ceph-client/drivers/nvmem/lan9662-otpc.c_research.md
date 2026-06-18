<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/lan9662-otpc.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/lan9662-otpc.c

## Purpose
Implements Microchip LAN9662 OTP controller access as a byte-addressable NVMEM provider with read and write support.

## Important APIs, Types, And Functions
`struct lan9662_otp` stores device and MMIO base. Helpers power the OTP block, wait for flags to clear, set byte addresses, execute commands, and read/write individual bytes. `lan9662_otp_read()` and `lan9662_otp_write()` provide NVMEM callbacks over 8192 bytes.

## Control Flow
Probe maps the controller and registers `lan9662-otp`. Reads power up the block, issue a read command per byte, check read-prohibited status, copy data, and power down. Writes power up, skip zero bytes, read current data, OR requested bits into current data, skip no-op writes, program bytes, check write-prohibited/fail bits, and power down.

## State And Persistence
Runtime state is MMIO base and device. OTP contents are permanent; writes only transition bits by ORing new data with existing data.

## Dependencies And Integration Points
Depends on platform/OF matching, MMIO polling, and NVMEM provider core. Consumers can read or program LAN9662 OTP bytes through standard NVMEM APIs.

## Risks
OTP writes are destructive. Power-up return values are ignored in read/write wrapper paths, which can hide power sequencing failures. There is no explicit lock around byte sequences, so concurrent readers/writers could interleave. Byte-wise access is slow but simple.

## Test Signals
Read full and partial ranges, read/write prohibited addresses, write zero no-op behavior, write OR semantics, timeout on busy/go flags, and power state after early errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/lan9662-otpc.c -->
