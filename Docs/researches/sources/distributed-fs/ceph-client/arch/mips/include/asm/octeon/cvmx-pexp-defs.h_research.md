# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pexp-defs.h

## Purpose
`cvmx-pexp-defs.h` is a pure CSR address header for the Octeon PCI Express packet/DMA complexes named NPEI and SLI. Unlike the PEM/PESC files, it does not define bitfield unions; it only gives symbolic addresses for many packet input/output, DMA, MSI, interrupt, memory-access, debug, scratch, state, and window-control registers.

## Important APIs, Types, And Functions
The API is the `CVMX_PEXP_NPEI_*` and `CVMX_PEXP_SLI_*` macro set. NPEI macros cover BAR1 indexes, BIST, control status, DMA channels, DMA doorbells and counts, packet input and output queues, instruction FIFO base/size/header registers, scatter-list FIFO registers, MSI receive/enable/map registers, RSL interrupt blocks, debug data/select, state, scratch, and memory window access. SLI macros mirror many of those functions under the SLI base, adding SLI-specific port control, MAC credit counters, packet control, S2M port controls, loopback/port kind registers, and transmit-pipe state.

## Control Flow
There is no local control flow. External code sequences these macros to initialize NPEI or SLI: set memory access/window registers, configure DMA channels and packet queues, enable packet input/output engines, set interrupt/MSI masks, and then poll counters or state registers. Indexed macros use masked offsets, typically for 2, 4, 8, 31, or 32 hardware slots.

## State And Persistence
All state is hardware-resident. Queue base-address, FIFO-size, doorbell, DMA count, MSI map, and interrupt-enable registers remain active until hardware reset or reprogramming. Packet and DMA counters represent device-side progress. The header does not define C storage or helper state.

## Dependencies And Integration Points
This file depends only on `CVMX_ADD_IO_SEG` and the broader Octeon CSR access model. It integrates with PCIe packet I/O, DMA engines, MSI interrupt routing, and packet input/output support. Higher-level code must pair these addresses with definitions from other CSR headers or raw 64-bit accesses.

## Risks
Because the file is address-only, callers lack typed bitfield protection and must know each register layout elsewhere. Masked indexed offsets can hide invalid queue/channel IDs. Some macros contain address aliases or generation-specific names, such as DMA state registers and MSI receive banks, so using the wrong NPEI versus SLI macro can touch a valid but unintended register. Register ordering and doorbell writes are side-effectful and can race with DMA or packet engines if memory barriers are missing in the caller.

## Test Signals
Good tests verify that each macro expands to the documented IO-segment address, especially indexed queue and DMA macros. Runtime signals include successful MSI delivery through receive/enable/map registers, packet queue doorbell progress, DMA count updates, interrupt summary/mask behavior, memory-window reads returning expected data, and stable state/debug register reads during bring-up and shutdown.
