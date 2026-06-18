# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu.h

## Purpose
`rvu.h` is the central private header for the OcteonTX2/CN10K RVU Admin Function driver. It defines PCI IDs, PF/VF encoding helpers, hardware capability models, per-block and per-function state, mailbox workqueue state, firmware-data layout, the top-level `struct rvu`, MMIO accessors, silicon capability helpers, channel helpers, and cross-file function prototypes for all AF subsystems.

## Important APIs, Types, and Functions
- PF/VF helpers include `rvu_make_pcifunc()`, `rvu_pcifunc_pf_mask()`, `rvu_get_pf()`, `is_vf()`, `is_pffunc_af()`, `is_lbk_vf()`, `is_pf_cgxmapped()`, and `is_cgx_vf()`.
- Core resource types include `struct rsrc_bmap`, `struct rvu_block`, and `struct rvu_pfvf`.
- `struct rvu_hwinfo` stores global hardware constants, channel bases, block descriptors, NIX/NPC resource containers, and capability flags in `struct hw_cap`.
- Mailbox/interrupt state is represented by `struct rvu_work`, `struct mbox_wq_info`, `struct rvu_irq_data`, and `struct mbox_ops`.
- `struct rvu_fwdata` mirrors firmware-provided platform data, including MAC addresses, clocks, MSI-X table base, PTP external clock/timestamp fields, channel data, alternate-AF notification info, and CGX LMAC firmware data.
- `struct rvu` is the top-level AF object containing BAR mappings, PCI device, hardware model, PF/VF arrays, locks, mailbox queues, FLR state, MSI-X state, CGX maps, firmware data, PTP pointer, devlink/debugfs, representor state, MCS/CPT locks, and CN20K extension pointer.
- MMIO accessors `rvu_write64()`, `rvu_read64()`, `rvupf_write64()`, `rvupf_read64()`, and `rvu_bar2_sel_write64()` centralize AF/PF BAR register access.
- Inline silicon helpers such as `is_rvu_otx2()`, `is_cn10kb()`, `is_cgx_mapped_to_nix()`, and `is_rvu_supports_nix1()` gate generation-specific behavior.
- Function prototypes expose RVU core, CGX, NPA, NIX, NPC, CPT, CN10K, MCS, switch, SDP, debugfs, and representor APIs to sibling files.

## Control Flow
The header itself contains only inline helper control flow. Runtime flow is implemented in `rvu.c` and subsystem files. Its helper functions are used throughout initialization, mailbox handling, channel calculation, PF/VF validation, block lookup, CGX permission checks, and generation-specific branching. The `MBOX_MESSAGES` macro expansion declares all mailbox handler prototypes, making mailbox dispatch in `rvu.c` compile-time synchronized with `mbox.h`.

## State and Persistence Behavior
The structures in this header describe all major in-memory state for the AF driver. Hardware ownership is mirrored in resource bitmaps, LF-to-`pcifunc` maps, PF/VF counters, MSI-X maps, NIX/NPA/NPC structures, and CGX/PF maps. Firmware data is memory-mapped platform state, not allocated by the driver. No disk persistence exists. Hardware configuration persists in CSRs until FLR, block reset, or device removal, while software mirrors are rebuilt at probe.

## Dependencies and Integration Points
The header includes Linux PCI/devlink/silicon helpers and RVU-local headers for structures, devlink, common definitions, mailbox messages, NPC, registers, and PTP. It is included by most AF implementation files and is the main integration point between independent subsystems such as NIX, NPA, NPC, CPT, CGX/RPM, MCS, SDP, switchdev-like representors, debugfs, and CN10K/CN20K support.

## Risks and Edge Cases
- `struct rvu_fwdata` must stay exactly aligned with firmware; `FWDATA_CGX_LMAC_OFFSET` and reserved fields make this fragile.
- PF/VF bit layout changes for CN20K are handled by inline helpers; callers must use helpers rather than hard-coded shifts.
- Many prototypes accept raw `u16 pcifunc` and `void *` subsystem handles, so validation has to happen at API boundaries.
- `struct rvu_pfvf` carries many subsystem-owned fields; teardown ordering must respect ownership to avoid leaks or stale hardware state.
- Channel helpers assume NIX constants are readable from NIX0 and that programmable channel bases have already been initialized.
- Header-level inline helpers read MMIO in some cases, so they are not side-effect-free predicates.

## Test Signals
- Compile coverage across OcteonTX2, CN10K, CN20K, debugfs enabled/disabled, and all mailbox handler declarations.
- Static analysis for direct PF/VF shift/mask use outside helper functions.
- Firmware ABI tests validating `struct rvu_fwdata` size, offset, magic, version, and CGX LMAC union layout.
- Unit or mock tests for channel helpers under programmable and non-programmable channel modes.
- Probe/FLR teardown tests that watch all `struct rvu_pfvf` counters and bitmaps return to zero.
