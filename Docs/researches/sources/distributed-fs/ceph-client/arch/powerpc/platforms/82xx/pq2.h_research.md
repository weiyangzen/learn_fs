# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/pq2.h

## Purpose
`pq2.h` declares common PowerQUICC II platform helpers for 82xx board files.

## Important APIs, Types, and Functions
It declares `pq2_restart()`. When PCI is enabled it declares `pq2ads_pci_init_irq()` and `pq2_init_pci()`; otherwise it provides no-op inline stubs.

## Control Flow, State, and Persistence
The header owns no state. The stubs allow board code to compile without PCI conditionals around helper calls.

## Dependencies and Integration Points
It integrates common PQ2 code with board support and optional PCI support that may live elsewhere in the platform tree.

## Risks and Test Signals
Risks include unused or externally defined PCI declarations drifting from implementation. Test signals are PCI and non-PCI board builds, and link coverage for `pq2_restart()`.
