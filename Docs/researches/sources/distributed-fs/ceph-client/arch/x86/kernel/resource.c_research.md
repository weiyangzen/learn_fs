# sources/distributed-fs/ceph-client/arch/x86/kernel/resource.c

## Purpose
Filters candidate x86 memory resources so PCI/resource allocation avoids BIOS ROM and, optionally, E820-reserved ranges.

## APIs, Types, And Functions
Public function is `arch_remove_reservations(struct resource *avail)`. Helpers are `resource_clip()` and `remove_e820_regions()`.

## Control Flow
For memory resources, `arch_remove_reservations()` clips out the high BIOS ROM window, then `remove_e820_regions()` iterates E820 entries if `pci_use_e820` is set. Each overlap shrinks `avail` to keep the larger non-conflicting side, logging the avoided E820 range and remaining range when it changes.

## State And Persistence
This code mutates the caller-provided `struct resource` in place. It does not own persistent state; it reads global E820 and PCI policy.

## Dependencies And Integration
Depends on `e820_table`, BIOS ROM constants, `pci_use_e820`, and generic resource allocation. It protects PCI resource assignment from firmware/BIOS memory conflicts.

## Risks And Test Signals
Clipping keeps only one side of a conflict, so it can discard usable subranges in complex overlaps. Wrong E820 data can overly constrain PCI BAR placement. Test signals include PCI resource allocation logs, absence of allocations inside BIOS/E820 reserved regions, and device enumeration on systems with fragmented firmware memory maps.
