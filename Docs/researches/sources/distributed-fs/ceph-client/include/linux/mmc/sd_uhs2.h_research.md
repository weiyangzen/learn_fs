# sources/distributed-fs/ceph-client/include/linux/mmc/sd_uhs2.h

## Purpose
`mmc/sd_uhs2.h` defines SD UHS-II packet, command, response, message, register, capability, setting, and clock constants. It is the protocol vocabulary used by host and card code that initializes and operates UHS-II cards.

## Important APIs, Types, And Functions
The header defines link-layer packet fields (`UHS2_NATIVE_PACKET`, packet type, source/destination IDs, transaction ID), message categories/codes, native CCMD/DCMD read/write and payload length fields, device init/enumeration/config payload and response lengths, response NACK/error codes, device register IO addresses, SD application packet bits, device configuration register offsets, generic/PHY/link capability and setting masks, interrupt/status/command register offsets, dormant and init-complete bits, and `UHS2_RCLK_MAX`/`UHS2_RCLK_MIN`.

## Control Flow And State
No state is stored here. Initialization code builds native packets using the header and argument bitfields, reads generic/PHY/link capabilities, writes selected settings, waits for device initialization and enumeration responses, enables interrupts and clocks, and optionally enters dormant/hibernate states. Data transfer setup uses DCMD transfer mode bits such as half-duplex and length mode.

## Dependencies And Integration Points
It relies on common bit macros from surrounding kernel headers and is included by `host.h`. Integration points include UHS-II host controller operations, `struct uhs2_command` in `core.h`, UHS-II card config in `card.h`, SD application command transport, and host timing constants.

## Risks And Test Signals
Risks include bit-position mistakes in packet assembly, response length mismatch, unsupported lane/speed setting selection, mishandled NACK error codes, and clocks outside UHS-II reference limits. Test signals include UHS-II initialization traces, capability/register decode tests, packet encode/decode tests, dormant/resume tests, interrupt enable/disable tests, and hardware or emulator validation for speed A/B and half-duplex modes.
