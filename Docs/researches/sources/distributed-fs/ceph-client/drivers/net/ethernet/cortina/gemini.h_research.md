# sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/gemini.h

## Purpose
`gemini.h` defines the register map, queue IDs, descriptor formats, bit masks, and packed union views used by the Cortina/StorLink Gemini GMAC driver.

## Important APIs, types, and functions
- Queue/register constants define TOE/non-TOE queue headers, software/hardware free queues, per-GMAC TX/default queues, global interrupt/status/enable/select registers, DMA registers, GMAC registers, and queue pointer helpers.
- `GET_WPTR()`, `GET_RPTR()`, `SET_WPTR()`, `SET_RPTR()`, and `RWPTR_*` macros manipulate packed ring pointers.
- Interrupt bit macros cover TX/RX data/protocol errors, TX EOF/FIN, default queues, TOE/class queues, MIB, pause, overrun, and freeq-empty events.
- Descriptor unions and structs define `gmac_txdesc` and `gmac_rxdesc` word layouts, including buffer size, status, checksum status, byte count, DMA address, SOF/EOF, TSO/MTU/checksum bits, RX offsets, and error bits.
- Config/status unions define DMA control, TX weights, queue thresholds, RX filter, GMAC config0-3, and PHY link status.
- Error/status helper macros classify RX length, overrun, CRC, and frame errors.
- Queue header structures define non-TOE queue base/size and read/write pointer words.

## Control flow and state
The header has no executable driver lifecycle, but its unions are used as typed register/descriptor snapshots throughout `gemini.c`. Hardware and software state are encoded in ring pointer registers, descriptor SOF/EOF bits, interrupt status/enable registers, and GMAC config/status registers.

## Dependencies and integration points
It depends on Linux bitops and is tightly coupled to the Gemini hardware manual and `gemini.c`. The Kconfig-selected driver uses these constants for all MMIO programming and descriptor parsing.

## Risks and test signals
Risks are register offset errors, bitfield layout/compiler assumptions, pointer wrap mistakes, and descriptor status interpretation bugs. Runtime tests should cover RX/TX descriptor dumps, interrupt routing, checksum status classification, multicast filter programming, MTU/config0 max-length selection, and ring wrap.
