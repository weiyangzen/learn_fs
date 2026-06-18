# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-regs.h

## Purpose
Defines the EIP93 packet engine register map, bitfields, SA record layout, SA state layout, and descriptor layout used by the EIP93 driver.

## Important APIs, Types, and Functions
Register definitions cover direct packet engine registers, command/result ring registers, packet engine config/status, endian and clock control, option/revision registers, interrupt registers, SA command words, and state offsets. Important bitfields include ownership/ready bits, extended error codes, ring sizes/counts, clock enables, algorithm option bits, interrupt masks, SA cipher/hash/mode/opcode fields, and copy/HMAC controls.

The hardware-facing packed structures are `struct sa_record`, `struct sa_state`, and `struct eip93_descriptor`.

## Control Flow
`eip93-main.c` uses these definitions for initialization, interrupt control, option detection, and result draining. `eip93-common.c`, `eip93-cipher.c`, `eip93-aead.c`, and `eip93-hash.c` use SA command fields and descriptor fields to program work for the packet engine.

## State and Persistence
No software state is held in the header. The packed structures define DMA-visible state exchanged with hardware: SA records contain command words, keys, digest state, SPI/sequence fields, and nonce; SA state stores IV, byte count, and intermediate digest; descriptors carry control/status, source/destination/SA/state addresses, user ID, and length.

## Dependencies and Integration Points
Uses Linux `BIT`, `GENMASK`, and `FIELD_PREP` bit helpers through including C files. It is tightly coupled to the EIP93 hardware manual and must match hardware endianness/address expectations.

## Risks
Packed structure layout and bit constants are hardware ABI. Typos or field-width mistakes can cause silent crypto corruption, DMA faults, or incorrect error reporting. `EIP93_REG_INT_MASK_STAT` and `EIP93_REG_INT_CLR` share offset `0x204`, so read/write semantics must remain clear. Descriptor address fields are 32-bit.

## Test Signals
Validate with hardware probe logs, register readback tests, crypto KATs across every mode, endian configuration tests, and hardware error injection to confirm `eip93_parse_ctrl_stat_err()` mappings.
