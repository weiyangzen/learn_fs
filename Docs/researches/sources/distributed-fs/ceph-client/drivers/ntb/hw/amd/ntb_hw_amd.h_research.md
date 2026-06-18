# sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/ntb_hw_amd.h

## Purpose

This header defines AMD NTB register offsets, bit masks, constants, data structures, and helpers used by `ntb_hw_amd.c`. It captures the hardware contract for AMD NTB capability registers, side-info state, memory-window translation/limit registers, doorbells, events, SMU status, scratchpads, and link status fields.

## Important APIs, types, and functions

Important constants include `AMD_DB_CNT`, `AMD_MSIX_VECTOR_CNT`, `AMD_SPADS_CNT`, `AMD_CNTL_OFFSET`, `AMD_SIDEINFO_OFFSET`, memory-window limit and XLAT offsets, doorbell offsets, event masks, SMU offsets, and `AMD_PEER_OFFSET`. Link extraction macros are `NTB_LNK_STA_SPEED()` and `NTB_LNK_STA_WIDTH()`.

The header defines fallback `read64`/`write64` implementations using paired 32-bit MMIO operations when architecture `readq`/`writeq` are unavailable. `struct ntb_dev_data` describes per-device memory-window count, base BAR index, and endpoint flag. `struct amd_ntb_vec` links interrupt vectors to the driver state. `struct amd_ntb_dev` embeds `struct ntb_dev` and stores topology/status, capability counts, masks, MSI-X state, MMIO bases, scratchpad offsets, heartbeat work, and debugfs dentries.

The macros `ntb_ndev()` and `hb_ndev()` convert NTB/work pointers back to `amd_ntb_dev`. Forward declarations expose side-info and link-poll helpers across the C file.

## Control flow and state behavior

The header has no runtime flow but defines how runtime state is laid out and how register state is interpreted. The split of self and peer MMIO, local and peer scratchpads, and reserved event/doorbell masks is foundational for the C file's lifecycle and interrupt behavior.

## Dependencies and integration points

It depends on `linux/ntb.h` and `linux/pci.h`. The file is private to the AMD NTB hardware driver and should remain synchronized with AMD silicon register definitions and any new PCI ID capability data.

## Risks and edge cases

Fallback 64-bit MMIO writes are not atomic because they are implemented as two 32-bit writes; callers should only use them where hardware tolerates that sequence. Register offsets and bit definitions are hard-coded, so platform variants with different layout require new capability data or code changes. `struct ntb_dev_data` uses small integer types, so counts and BAR shifts must remain within expected bounds.

## Test signals

Compile tests on architectures with and without native `readq/writeq` validate fallback paths. Runtime tests through `ntb_hw_amd.c` should verify register offsets, event masks, scratchpad counts, BAR mapping, and link speed/width extraction.
