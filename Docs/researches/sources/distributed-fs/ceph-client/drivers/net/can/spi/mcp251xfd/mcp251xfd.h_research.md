# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd.h

Purpose: Central private header for the MCP251xFD driver, defining registers, bit masks, SPI command formats, hardware object layouts, ring/private state structures, inline helpers, quirk flags, model IDs, and cross-file prototypes.

Important APIs, types, and functions: Key types include hardware TEF/TX/RX objects, SPI command buffers, regmap transfer buffers, TEF/TX/RX rings, ECC/status structs, model/devtype types, and `struct mcp251xfd_priv`. Inline helpers build SPI commands, compute RAM addresses, convert timestamps to SKB hwtstamps, inspect model/mode state, and compute ring head/tail/free/linear lengths.

Control flow: No standalone flow, but it shapes every driver path: core owns `mcp251xfd_priv`, regmap uses command helpers, ring/RX/TEF/TX use address and ring arithmetic helpers, and timestamp users call SKB timestamp helpers.

State and persistence behavior: `mcp251xfd_priv` holds all volatile driver state including CAN core/offload/netdev, regmaps and buffers, SPI speeds, rings, workqueue, flags, coalescing, ECC/status, timestamp counters, GPIO/clock/regulator handles, devtype quirks, saved bus error counters, and optional GPIO chip.

Dependencies and integration points: Includes Linux CAN, netdevice, regmap, SPI, GPIO, regulator, timecounter, and workqueue APIs. It is the internal contract among all MCP251xFD units and gates devcoredump availability.

Risks: Register bits and object layouts must match silicon. Ring arithmetic assumes power-of-two counts. Packed/cacheline-aligned command buffers are sensitive to layout changes. Quirk bits control CRC/ECC/half-duplex behavior across the driver.

Test signals: Build with sparse/packed warnings, hardware smoke tests for all models/quirks, CRC/nocrc and CAN/CAN-FD layouts, and RX/TX timestamp/ring helper coverage.
