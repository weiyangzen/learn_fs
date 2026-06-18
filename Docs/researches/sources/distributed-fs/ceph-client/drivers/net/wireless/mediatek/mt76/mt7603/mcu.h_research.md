# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mcu.h

## Purpose
MT7603 MCU command/response descriptor definitions, packet constants, firmware download address, command IDs, extended command IDs, and extended event IDs.

## Important APIs, Types, And Functions
- `struct mt7603_mcu_txd` defines the packed command header: length, port/queue, command ID, packet type, set/query mode, sequence, extended command fields, and reserved words.
- `struct mt7603_mcu_rxd` defines response/event fields used for sequence matching and extended event identification.
- `MCU_PKT_ID`, `MCU_PORT_QUEUE`, `MCU_PORT_QUEUE_FW`, and `MCU_FIRMWARE_ADDRESS` define packet routing and firmware target address.
- Query mode enum defines query, set, reserved, and not-applicable values.
- Base command enum includes target address/length, firmware start/scatter/restart, patch commands, loopback/channel privilege, register access, and extended command wrapper.
- Extended command/event enums name channel switch, efuse buffer mode, txpower control, power saving, beacon update, EDCA, thermal, and related firmware operations.

## Control Flow
Header-only constants are consumed by `mcu.c` when framing commands and interpreting responses. Negative command IDs in `mcu.c` map to base commands; positive IDs are wrapped as `MCU_CMD_EXT_CID`.

## State And Persistence
No direct state. It defines the host/firmware ABI for command SKBs and response SKBs.

## Dependencies And Integration Points
Used by mt7603 MCU implementation and indirectly by DMA RX event routing. It must align with firmware command ABI and firmware image expectations.

## Risks
Packed layout or command-ID mistakes can make firmware ignore commands or misparse payloads. Response sequence field position is critical for timeout/retry logic. Reused command value `0x20` for loopback/channel privilege requires context-sensitive use.

## Test Signals
Firmware download/start, extended channel switch, efuse buffer upload, txpower command, and teardown restart are the main ABI tests. Trace raw MCU headers if firmware command timeouts appear.
