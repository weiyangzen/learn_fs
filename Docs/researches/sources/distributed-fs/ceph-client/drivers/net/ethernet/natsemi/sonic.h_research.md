# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/sonic.h

## Purpose
`sonic.h` defines the register map, bit fields, descriptor formats, ring sizing, private state, prototypes, and descriptor access helpers for the shared SONIC Ethernet core and its platform wrappers. It encodes the controller's 16-bit versus 32-bit bus modes and the endian-sensitive descriptor layout that `sonic.c` consumes.

## Important APIs, types, and functions
The header defines SONIC register offsets (`SONIC_CMD`, `SONIC_ISR`, `SONIC_RCR`, resource and CAM registers), command/config/status bits, interrupt masks, descriptor offsets for receive resources, receive descriptors, transmit descriptors, and CAM descriptors, ring constants, and `struct sonic_local`. Inline APIs include `sonic_buf_put()`, `sonic_buf_get()`, typed CDA/TDA/RDA/RRA accessors, CAM enable accessors, and receive-resource address/index helpers. It also declares the static functions implemented by `sonic.c`.

## Control flow
The header itself has no runtime control flow, but it controls how runtime code indexes and writes coherent descriptor memory. `SONIC_BUS_SCALE()` changes descriptor spacing between 16-bit and 32-bit bus modes. Wrappers include this header, define `SONIC_READ()`/`SONIC_WRITE()`, then include `sonic.c`, causing these constants and inline helpers to become the compile-time contract for the shared implementation.

## State and persistence
`struct sonic_local` is the main state contract. It tracks DMA bit mode, register offset, descriptor memory and sub-areas, SKB rings, DMA addresses, RX/TX indices, EOL markers, message level, backing device, stats, and lock. The header also embeds hardware sizing choices: 16 receive resources/descriptors, 16 transmit descriptors, 1520-byte default receive buffers, and 16 CAM descriptors.

## Dependencies and integration points
The header depends on Linux netdevice, DMA address, SKB, and stats types through includers. It integrates platform wrappers with shared core code by exposing function prototypes and requiring wrapper-specific register macros. Its descriptor helpers use raw 16-bit access to preserve bus layout and endian expectations.

## Risks and edge cases
Comments warn that descriptor structures are endian and bus-size dependent. Incorrect `dma_bitmode`, `reg_offset`, or bus scaling corrupts descriptor interpretation. The descriptor page must not cross a 64K boundary, which `sonic_alloc_descriptors()` relies on through page-sized coherent allocation. `sonic_rr_entry()` truncates through 16-bit resource addresses, matching SONIC hardware but requiring descriptor memory placement within the expected logical range. Changing ring sizes requires preserving power-of-two masks and descriptor memory layout.

## Test signals
The header is validated indirectly by building and running each SONIC wrapper in 16-bit and 32-bit modes. Useful signals include correct descriptor addresses programmed into RRA/RDA/TDA, successful CAM loading, RX/TX operation on big-endian and little-endian configurations, and absence of descriptor corruption when multicast or timeout paths manipulate EOL bits.
