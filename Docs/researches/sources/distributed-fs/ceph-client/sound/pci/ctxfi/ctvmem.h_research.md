# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctvmem.h

## Purpose

This header defines ctxfi device virtual-memory structures for mapping host PCM buffers into the card's logical address space.

## Important APIs, types, and functions

It defines `CT_PTP_NUM`, `CT_PAGE_SIZE`, `CT_PAGE_SHIFT`, alignment macros, `struct ct_vm_block`, and `struct ct_vm`. `struct ct_vm` owns page-table DMA buffers, used/free lists, a mutex, and `map`, `unmap`, and `get_ptp_phys` callbacks. It declares `ct_vm_create()` and `ct_vm_destroy()`.

## Control flow

ATC creates a VM object during hardware setup, maps substream buffers during PCM preparation, and supplies the page-table physical address to hardware initialization.

## State and persistence behavior

The defined state persists for the card lifetime and for each mapped PCM buffer. Hardware consumes the page-table pages while transport is active.

## Dependencies and integration points

It depends on Linux mutex/list/PCI APIs and ALSA memalloc. It is integrated with `cthw20k2.c` transport setup and ATC PCM resource management.

## Risks and test signals

Page-size assumptions and map/unmap ordering are the main risks. Build tests plus repeated SG buffer mapping under playback/capture load give the strongest signal.
