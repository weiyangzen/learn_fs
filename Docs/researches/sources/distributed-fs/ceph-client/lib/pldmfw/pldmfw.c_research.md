# sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw.c

## Purpose
Implements a PLDM firmware package parser and firmware flashing coordinator for drivers that consume DMTF DSP0267-formatted images.

## APIs, Control Flow, and State
Exports `pldmfw_flash_image()` and `pldmfw_op_pci_match_record()`. `struct pldmfw_priv` tracks firmware pointer, parse offset, records, components, header metadata, bitmap sizes, CRC, and the selected record. The flash flow allocates private state, parses the image, finds a matching record via driver ops, optionally sends package data, sends component table entries with start/middle/end flags, flashes matching components, finalizes update, and frees all parsed records/components. Parsing validates header UUID/revision, header size, component bitmap length, record lengths, descriptor TLV lengths for standard descriptors, component offsets/sizes, selected single-component mode, total header size, and CRC32. PCI match extracts vendor/device/subsystem descriptors and compares them against `struct pci_dev`, treating zero descriptor values as wildcards.

## Dependencies, Integration, Risks, and Tests
Depends on firmware loader data, device logging, PCI helpers, UUID, unaligned little-endian access, CRC32, bitmaps, lists, and `linux/pldmfw.h`. Drivers provide callbacks for record matching, package data, component tables, flashing, and finalization. Risks include malformed images exercising variable-length pointer iteration, partial allocations before parse failure, single-component mode skipping allocations without freeing skipped component structs, callback failures mid-update, wildcard PCI matching surprises, and unaligned field misuse. Test signals include PLDM image fuzzing, CRC mismatch tests, malformed TLV/record/component length tests, PCI descriptor matching matrices, single-component selection tests, and driver callback failure injection.
