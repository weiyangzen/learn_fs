# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_mmu.h

## Purpose
Defines GH100 MMU descriptor bitfields for PTEs, version-3 PDEs, dual PDEs, and version-3 PTEs.

## Important APIs, Types, And Functions
Key fields include PTE aperture, kind, valid, PCF, address, peer ID, and descriptor sizes. PDE fields encode valid/is-PTE, aperture, page-cache/ATS behavior, address, and separate big/small page fields for dual PDEs.

## Control Flow
No executable flow. VMM code uses these definitions to construct page-table entries and directory entries, then submits them to MMU memory.

## State And Persistence
No software state is stored in the header. Encoded descriptors persist in GPU page tables and control memory translation until unmapped or overwritten.

## Dependencies And Integration Points
Consumed by Nouveau VMM/MMU backends, `nvhw/drf.h` multi-word helpers, and memory-map code handling VRAM, peer, coherent, and non-coherent system memory.

## Risks
Descriptor bitfields are high-impact. Wrong aperture, valid bit, PCF, address shift, kind, or peer ID can cause GPU page faults, memory corruption, or cache-coherency bugs.

## Test Signals
VMM map/unmap tests, GPU page-fault logs, sparse mappings, ATS/coherency behavior, peer memory tests, and memory-kind validation are the important signals.
