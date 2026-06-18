# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_qs.h

## Purpose
Defines Queue System extraction/injection register and field macros used by Ocelot CPU port and FDMA paths.

## Important APIs/types/functions
Macros cover extraction EOF/pruned/abort/escape/not-ready status words and valid-byte decoding; extraction group config/read/pruning/config; injection group config/write/control/status/error; and fields for mode, byte swap, gap size, SOF/EOF/abort, FIFO ready, in-progress, and sticky errors.

## Control flow, state, persistence
No executable flow. Runtime state is QS hardware register state. In this subset, `ocelot_fdma_start` programs group 0 into DMA mode with these macros.

## Dependencies and integration
Consumed by `ocelot_fdma.c` and wider Ocelot queue-system injection/extraction code. Relies on standard `BIT`/`GENMASK` macro availability through includes.

## Risks and test signals
Header notes big-endian handling is TODO. Wrong mode or byte-swap fields would break CPU traffic. Test FDMA and non-FDMA RX/TX, valid-byte endings, abort/pruned extraction, and endian-sensitive platforms.
