# Group Research: group_12_9front_sources_os_plan9_9front_sys_src_9_pc_etherga620_c_sources_os_p_d5db8cc31558

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`.

Read coverage: completed full-file reads for both listed files.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherga620.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherga620.c

## Purpose

This file is the Plan 9/9front PCI ethernet driver for Netgear GA620, GA620T, Alteon AceNIC, DEC DEGPA-SA, and SGI AceNIC adapters built around the Alteon Tigon 2 gigabit ethernet controller. It provides the host-side driver glue, PCI discovery, device reset, firmware upload, ring setup, interrupt handling, transmit/receive paths, link-state handling, EEPROM MAC address reads, and generic `Ether` registration.

It includes `etherga620fw.h` directly and loads the embedded Tigon2 firmware into NIC local memory during reset.

## Main Interfaces

- `etherga620link()` registers card name `GA620` with the generic ethernet layer via `addethercard`.
- `ga620pnp()` binds an unused detected controller to an `Ether`, initializes hardware, installs callbacks, and enables interrupts.
- `ga620transmit()`, `ga620interrupt()`, `ga620receive()`, `ga620ctl()`, `ga620ifstat()`, `ga620promiscuous()`, `ga620multicast()`, and `ga620shutdown()` are the operational driver hooks.
- `ga620pci()` scans PCI devices and builds the controller list.
- `ga620reset()` and `ga620init()` split hardware reset/firmware-load work from runtime ring and mailbox initialization.

## Core Data Structures

The driver models the Tigon host/NIC ABI explicitly:

- `Host64` stores high/low halves of PCI-visible host addresses.
- `Ere` is an event ring element.
- `Rbd` is used for receive descriptors and receive-return descriptors, including an `opaque` pointer that carries the Plan 9 `Block*`.
- `Sbd` is a send descriptor.
- `Rcb` is a firmware ring-control block.
- `Gib` is the General Information Block shared with firmware, containing statistics, all ring control blocks, and host-addressed producer/consumer pointer locations.
- `Ctlr` holds PCI identity, MMIO base, MAC address, shared structures, ring pointers, ring indexes, counters, and tunables.

The ring sizes are fixed to the firmware/NIC interface: 256 event entries, 64 command entries, 512 send entries, 512 standard receive entries, 256 jumbo receive entries, 1024 mini receive entries, and 2048 receive-return entries. Jumbo and mini receive rings are disabled by the high/low fill levels and by `RingDisabled` controls.

## Control Flow

PCI discovery in `ga620pci()` matches ethernet-class PCI devices against known vendor/device IDs, maps BAR0 with `vmap`, enables PCI, calls `ga620reset()`, enables bus mastering, and queues each controller on `ctlrhead`.

Reset in `ga620reset()` hard-resets the adapter, forces little-endian operating mode, configures SRAM and PCI state, reads the station address from the AT24C32 serial EEPROM, and uploads firmware sections:

- text to `tigon2FwTextAddr`
- rodata to `tigon2FwRodataAddr`
- data to `tigon2FwDataAddr`
- zeroed sbss and bss regions

Runtime initialization in `ga620init()` programs the MAC address, allocates the GIB and host rings, writes ring control blocks, configures DMA, coalescing, link negotiation, MTU, interrupt masks, and finally starts firmware by writing `CPUApc` and clearing `CPUhalt`.

Transmit in `_ga620transmit()` first frees completed send blocks using the firmware-updated send consumer index, then drains `edev->oq` into available send descriptors, records each `Block*` in `ctlr->srb`, and updates `Spi`.

Receive in `ga620receive()` walks the receive-return ring until `rrrci == rrrpi[0]`, delivers valid standard-frame blocks with `etheriq`, frees errored blocks, clears descriptor opacity, decrements the matching receive-ring fill count, and advances the consumer index. `ga620replenish()` tops the standard receive ring back to `NrsrHI`.

Interrupt handling in `ga620interrupt()` acknowledges ownership through `Hi`, loops over receive, transmit completion, event processing, and receive replenishment until no more work is found, then unmasks/clears the host interrupt. It measures handler cycles into `ctlr->ticks`.

Firmware events in `ga620event()` handle operational startup, statistics refresh, link-state changes, and unknown/error events. On firmware-up, the driver sends commands to mark the host stack up and start link negotiation.

## Configuration and Diagnostics

`ga620ctl()` accepts runtime text commands:

- `coalupdateonly on|off`
- `hardwarecksum on|off`
- `rct <n>`
- `sct <n>`
- `st <n>`
- `smcbd <n>`
- `rmcbd <n>`

`ga620ifstat()` dumps nonzero firmware statistics and driver counters/tunables. Promiscuous mode sends command `0x0a`; multicast add enables multicast reception with command `0x0e`. The multicast hook does not track individual multicast addresses and does nothing on removal.

## Dependencies

This is tightly coupled to the Plan 9 PC kernel ethernet stack and PCI support:

- `etherif.h`, `netif.h`, `pci.h`, `io.h`, `dat.h`, `fns.h`
- Plan 9 block queues and packet delivery: `qget`, `Block`, `freeb`, `iallocb`, `etheriq`
- PCI and MMIO helpers: `pcimatch`, `pcienable`, `pcisetbme`, `pcicfgw8`, `vmap`
- CPU timing and delays: `cycles`, `microdelay`
- Firmware constants and arrays from `etherga620fw.h`

## Notable Risks

- `ga620init()` allocates GIB/rings with `malloc`/`malign` but does not check each allocation before writing through pointers.
- `ctlr->gib` is allocated with `malloc` rather than explicit zeroing, so correctness depends on allocator behavior or firmware overwriting relevant fields.
- `ctlr->srb` is allocated with `malloc`; `_ga620transmit()` expects unused entries to be `nil` when freeing completions.
- `ga620pci()` leaks a mapped BAR if `Ctlr` allocation fails after `vmap`.
- `ga620shutdown()` prints unconditionally, which can be noisy during normal shutdown.
- Runtime `ga620ctl()` mutates firmware ring-control fields without explicit synchronization against interrupts or firmware access.
- Hardware checksum toggles only update ring-control flags; existing descriptors or firmware state are not drained/reinitialized.
- Jumbo and mini rings are disabled; the driver is standard-MTU only despite supporting Tigon2 gigabit hardware.
- EEPROM access is bit-banged by command strings; malformed strings return `-1`, but call sites assume the hardcoded protocol is correct.
- The interrupt loop uses a fixed two-pass idle check; unusual firmware producer update races could delay work until a later interrupt.
- Firmware is opaque generated data, so source-level auditing of NIC behavior is not possible from this file alone.

## Testing Notes

No executable tests were run for this research pass. Useful verification would require real supported PCI hardware or an emulator/model with Tigon2 register behavior. Static checks should focus on allocation failure paths, ring index invariants, interrupt masking, and whether checksum/offload control changes need quiescing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherga620.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherga620fw.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherga620fw.h

## Purpose

This header is a generated embedded firmware image for the Alteon Tigon 2 controller used by `etherga620.c`. It is not a normal C API header; it defines firmware metadata and three static integer arrays containing compiled firmware text, read-only data, and initialized data. The host driver writes these arrays into NIC local memory and then starts CPU A at the firmware start address.

The file begins with `/* Generated by genfw.c */`, so the authoritative source was likely firmware object data transformed into C arrays.

## Exported Definitions

Firmware version:

- `tigon2FwReleaseMajor = 0x0c`
- `tigon2FwReleaseMinor = 0x04`
- `tigon2FwReleaseFix = 0x0b`

Firmware layout:

- `tigon2FwStartAddr = 0x00004000`
- `tigon2FwTextAddr = 0x00004000`
- `tigon2FwTextLen = 0x11bc0` bytes
- `tigon2FwRodataAddr = 0x00015bc0`
- `tigon2FwRodataLen = 0x10d0` bytes
- `tigon2FwDataAddr = 0x00016cc0`
- `tigon2FwDataLen = 0x1c0` bytes
- `tigon2FwSbssAddr = 0x00016e80`
- `tigon2FwSbssLen = 0xcc` bytes
- `tigon2FwBssAddr = 0x00016f50`
- `tigon2FwBssLen = 0x20c0` bytes

Static arrays:

- `tigon2FwText[]` starts at line 16 and contains the firmware instruction image.
- `tigon2FwRodata[]` starts at line 4558 and contains embedded strings, tables, and addresses.
- `tigon2FwData[]` starts at line 4829 and contains initialized firmware data.

The generated arrays include one trailing word beyond the declared load length for each loaded section. The driver copies only the explicit `*Len` byte count, so the trailing generated word is not part of the loaded section size.

## Integration With Driver

`etherga620.c` includes this header and calls `ga620lmw()` during `ga620reset()` to copy:

- `tigon2FwText` into `tigon2FwTextAddr`
- `tigon2FwRodata` into `tigon2FwRodataAddr`
- `tigon2FwData` into `tigon2FwDataAddr`
- zeroes into `tigon2FwSbssAddr` and `tigon2FwBssAddr`

After host-side GIB/ring setup in `ga620init()`, the driver writes `tigon2FwStartAddr` into `CPUApc` and releases CPU A from halt. The firmware then owns the NIC-side half of event, send, receive, command, stats, link, and DMA handling.

## Observed Contents

The text array is mostly 32-bit machine words. Its instruction patterns and register constants show extensive interaction with Tigon local registers, ring pointers, DMA state, PHY/link registers, and statistics counters. Because it is already compiled firmware, function names and types are not directly present.

The rodata array contains many embedded ASCII strings packed as 32-bit values. Visible strings include firmware provenance/version fragments, source path fragments such as `/projects/rcs/sw/ge/./nic/fw2/common/`, module names including `fwmain.c`, `timer.c`, `command.c`, `mcast.c`, `dma.c`, `data.c`, `mem.c`, `send.c`, `recv.c`, `mac.c`, and `cksum.c`, diagnostic names, command/link labels, DMA labels, receive/transmit names, and firmware build/compiler markers.

Visible build metadata includes `FW_VERSION: #1 Fri Apr 7 17:57:52 PDT 2000`, compile time `17:57:52`, compile user `devrcs`, compile host `compute`, compile domain `eng.acteon.com`, and compiler `gcc version 2.7.2`.

The data array contains small initialized configuration/state values, including ASCII fragments for `Alteon AceNIC V`, fixed address-like constants, and default table values used after firmware load.

## Functional Role In The System

From the host driver contract and visible firmware strings/tables, this image likely implements the NIC-resident side of:

- command-ring consumption
- event-ring production
- send-ring consumption
- receive-ring production and receive-return handling
- statistics maintenance
- link negotiation and link-state event generation
- DMA assist control
- packet classification/checksum assist behavior
- MII/GMII/PHY operations
- error/event reporting back to the host

The host driver depends on this firmware to update producer/consumer indexes in host memory and to interpret the GIB/Rcb layout exactly as declared in `etherga620.c`.

## Dependencies and Assumptions

This header assumes:

- Inclusion into exactly one driver translation unit, because the arrays are `static int`.
- A 32-bit `int` layout matching the firmware generator output.
- The host driver will copy byte lengths exactly as defined by the `*Len` macros.
- The target NIC local-memory ABI matches the hardcoded addresses.
- The host driver zeroes sbss and bss itself, since no arrays are provided for those sections.

The header has no include guards. That is acceptable for current use because it is included only by `etherga620.c`, but it would duplicate large static arrays if included elsewhere.

## Notable Risks

- The firmware is opaque binary data in C syntax, so normal source review cannot prove memory safety, packet parsing correctness, or link-state behavior.
- The generated arrays are typed as `int`; portability depends on Plan 9 kernel assumptions that `int` is 32 bits and stored in the expected endian form when written through `ga620lmw()`.
- The driver copies byte lengths, not array element counts. Any mismatch between macro lengths and array contents would cause truncated or overrun firmware loads.
- There is no checksum, signature, or runtime validation of the embedded firmware image before upload.
- The file embeds historical firmware provenance strings and generated binary contents; manual edits would be high risk and hard to review.
- The lack of include guards is harmless for the current direct include pattern but fragile if reused.

## Maintenance Notes

Treat this file as generated artifact data. Changes should come from the firmware source/object and `genfw.c`, then be validated by comparing section lengths, load addresses, and adapter boot behavior. Review of host/firmware compatibility should focus on the GIB layout, ring descriptor layouts, mailbox/register constants, and command/event code meanings shared with `etherga620.c`.

## Testing Notes

No firmware execution tests were run for this research pass. Practical validation requires supported Tigon2 hardware or a sufficiently accurate hardware model. Static validation can still check that all `tigon2Fw*Len` values are 4-byte aligned where copied as words, that the driver copies all declared sections, and that start/text/data addresses do not overlap unexpectedly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherga620fw.h -->