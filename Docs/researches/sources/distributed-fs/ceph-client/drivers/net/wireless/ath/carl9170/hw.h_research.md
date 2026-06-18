# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/hw.h

## Purpose

`hw.h` is the shared AR9170 hardware register and constant map. It names UART, timer, MAC, DMA, CAM, beacon, random, GPIO, memory controller, SPI, EEPROM, interrupt, power, USB, PTA bridge, SRAM/PRAM, endpoint, FIFO, TX queue, stream, ACK table, virtual MAC, and bitfield helper definitions.

## Important APIs, Types, and Functions

The file is macro-heavy rather than function-heavy. Major groups include `AR9170_MAC_REG_*` and related bit masks for timing, RX/TX counters, filters, CAM, QoS, AMPDU, DMA, beaconing, and encryption; USB endpoint/FIFO/DMA registers; EEPROM/SPI control registers; power/reset/clock registers; PTA bridge registers; memory bounds; endpoint constants; CPU clock and endpoint/fifo/queue enums; `struct ar9170_stream`; and `SET_VAL`, `SET_CONSTVAL`, `MOD_VAL`, `GET_VAL` bitfield helpers.

## Control Flow

The header has no runtime flow. It supplies constants for command, USB, MAC, PHY, debug, firmware validation, LED, EEPROM, and transport code. Register write batches in `mac.c` and `phy.c`, debug register ranges, firmware address validation, LED GPIO writes, and EEPROM reads all depend on these definitions.

## State and Persistence Behavior

Definitions here address persistent hardware state: MAC identity/BSSID, multicast hash, QoS parameters, encryption/CAM, DMA queue pointers, beacon timers and buffers, PHY reset through power registers, USB stream configuration, interrupt masks, GPIO LED state, EEPROM access, and hardware random numbers. `struct ar9170_stream` defines USB stream framing when firmware advertises streaming support.

## Dependencies and Integration Points

This is a shared driver/firmware hardware map included by debug, firmware, MAC, main, PHY, LED, transport, and command code. It depends on Linux `BIT()` and endian annotations through included driver headers.

## Risks and Edge Cases

Register constants are literal hardware ABI values; mistakes can write unrelated device blocks. Some comments mark undocumented or uncertain bits. The bitfield helpers require a corresponding `_S` shift macro. Stream tags and endpoint sizing must match firmware and USB descriptors. Debug register write paths use address ranges derived from this map, so widening ranges increases risk.

## Test Signals

Hardware smoke tests should cover MAC init, DMA trigger, beacon programming, GPIO LED state, USB stream mode, EEPROM read, CAM/key writes, QoS register writes, and reset paths. Static validation should catch duplicate or malformed bitfield definitions and ensure memory bounds match firmware parser checks.
