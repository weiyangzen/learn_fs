# sources/distributed-fs/ceph-client/sound/firewire/packets-buffer.c

## Purpose

This shared helper allocates and destroys DMA-backed page buffers split into many fixed-size isochronous packet slots.

## Important APIs, types, and functions

`iso_packets_buffer_init()` allocates the packet descriptor array, aligns packet size to the L1 cache line, calculates packets per page and required pages, initializes a FireWire ISO buffer, and fills per-packet virtual buffer pointers and offsets. `iso_packets_buffer_destroy()` destroys the ISO buffer and frees descriptors. Both functions are exported for other FireWire sound modules.

## Control flow

Initialization fails with `-ENOMEM` on allocation failures and `-EINVAL` if aligned packet size exceeds a page. After successful `fw_iso_buffer_init()`, each packet index maps to a page plus an aligned offset. Error paths free only resources already acquired.

## State and persistence behavior

The persistent state is `struct iso_packets_buffer`: one `fw_iso_buffer` plus an array of packet descriptors. The caller owns lifecycle and must call destroy after successful init.

## Dependencies and integration points

It depends on Linux FireWire ISO buffer APIs, DMA direction, page mapping, and `kmalloc_objs()`. Consumers can submit packet offsets to FireWire ISO contexts.

## Risks and test signals

Risks include oversized packet sizes, offset arithmetic mistakes, resource leaks on partial failure, and cache-alignment assumptions wasting pages. Tests should cover several packet sizes/counts, DMA directions, failure injection for allocations, and destroy after init.
