# sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu.h

## Purpose

`fsl_pamu.h` defines the Freescale PAMU hardware register map, PAACE/OME descriptor formats, field masks, operation encodings, table sizes, and cross-file APIs used by the PAMU platform and IOMMU-domain code.

## Important APIs, Types, and Functions

- `set_bf` / `get_bf`: mask-and-shift helpers for descriptor bitfields.
- Register offsets: PAMU table pointer registers, error/status registers, capability/control registers, and debug registers.
- `struct pamu_mmap_regs`: compact view of the PAMU table base/limit MMIO block.
- `struct paace`: primary/secondary PAACE descriptor, including window base, address fields, destination attributes, translation modes, translated base, secondary pointer, and operation encoding.
- `struct ome`: 128-byte operation mapping entry used by indexed operation translation.
- Constants such as `PAACE_NUMBER_ENTRIES`, `SPAACE_NUMBER_ENTRIES`, `OME_NUMBER_ENTRIES`, `PAACT_SIZE`, `SPAACT_SIZE`, and `OMT_SIZE`.
- Exported prototypes: `pamu_domain_init`, `pamu_enable_liodn`, `pamu_disable_liodn`, `pamu_config_ppaace`, `get_stash_id`, `get_ome_index`, and `pamu_update_paace_stash`.

## Control Flow

This header is passive, but it shapes the control flow of the implementation. `fsl_pamu.c` uses the register offsets to program hardware and the descriptor macros to construct PAACE/OME entries. `fsl_pamu_domain.c` calls the declared functions to change LIODN table entries when devices attach to or detach from IOMMU domains.

## State and Persistence Behavior

The data structures mirror hardware-visible memory. PAACE and OME contents persist in allocated RAM while PAMU is enabled and are consumed by hardware through programmed physical base/limit registers. The header encodes fixed table sizes rather than discovering all limits dynamically; comments indicate PAACE sizing is hard-coded to accommodate U-Boot LIODNs.

## Dependencies and Integration Points

It includes Linux IOMMU and PCI headers plus `<asm/fsl_pamu_stash.h>` for cache-stash attributes. Its ABI is private to the kernel tree but shared between PAMU hardware setup and PAMU domain integration.

## Risks and Edge Cases

- Bitfield macros evaluate the value argument in a write expression and assume matching `*_SHIFT` symbols.
- `struct paace` layout must remain exactly hardware-compatible; padding or endian mistakes would corrupt translations.
- Fixed table entry counts can reject valid future LIODNs unless updated.
- Register and descriptor constants are opaque hardware encodings, so accidental reuse across primary/secondary fields is hard to detect at compile time.

## Test Signals

Build-time coverage should catch structure and prototype drift. Runtime validation should dump PAACE/OME entries for known LIODNs and verify register writes match the QorIQ PAMU manual, including field encodings for validity, permissions, stash ID, window size, translation mode, and operation mapping.
