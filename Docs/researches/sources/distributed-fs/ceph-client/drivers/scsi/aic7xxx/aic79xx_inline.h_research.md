# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_inline.h

## Purpose

`aic79xx_inline.h` provides small, OS-neutral inline helpers and forward declarations for the AIC79xx/AHD core. It is included by Linux OSM and PCI glue after the platform header has defined `struct ahd_softc`, register access primitives, SCB structures, and mode constants. The file deliberately keeps only thin helpers here: mode-state packing, name access, scatter/gather sizing, sense-buffer address access, and interrupt/core API declarations.

## Important APIs, Types, and Functions

- `ahd_name(struct ahd_softc *ahd)` returns `ahd->name` for diagnostics.
- `ahd_known_modes()`, `ahd_build_mode_state()`, and `ahd_extract_mode_state()` maintain and encode/decode the controller source/destination register window modes using `SRC_MODE_SHIFT`, `DST_MODE_SHIFT`, `SRC_MODE`, and `DST_MODE`.
- Sequencer-control declarations `ahd_set_modes()`, `ahd_save_modes()`, `ahd_restore_modes()`, `ahd_is_paused()`, `ahd_pause()`, and `ahd_unpause()` are implemented in the core and are used throughout PCI/proc/error-recovery paths before touching mode-dependent registers.
- `ahd_sg_size()` chooses `struct ahd_dma64_seg` when `AHD_64BIT_ADDRESSING` is set, otherwise `struct ahd_dma_seg`.
- `ahd_get_sense_buf()` and `ahd_get_sense_bufaddr()` expose per-SCB autosense storage and bus address.
- Hardware access and queue helpers are declared: `ahd_inw/outw`, `ahd_inl/outl`, `ahd_inq/outq`, `ahd_get_scbptr()`, `ahd_set_scbptr()`, SCB RAM reads, `ahd_lookup_scb()`, `ahd_queue_scb()`, and `ahd_intr()`.

## Control Flow and State

The file has no independent runtime flow. Its inline mode helpers mutate cached fields in `struct ahd_softc` so later core/OS code can avoid redundant mode reads or restore a previously saved mode pair. Sense helpers are pure accessors over `struct scb`. SG sizing depends on the adapter flags selected during PCI DMA mask negotiation.

## Dependencies and Integration Points

This header depends on the AHD core definitions from `aic79xx.h`, Linux platform typedefs from `aic79xx_osm.h`, and generated register constants. It is consumed by `aic79xx_osm.c`, `aic79xx_osm_pci.c`, `aic79xx_pci.c`, and `aic79xx_proc.c` to bridge Linux paths to core routines without duplicating platform-specific logic.

## Risks

- Mode-state helpers assume the encoded mode bit fields and shifts match the hardware/core constants; drift would corrupt register-window restoration.
- `ahd_sg_size()` is only correct if `AHD_64BIT_ADDRESSING` is set consistently with the DMA segment format used when building S/G lists.
- Sense-buffer helpers trust SCB allocation invariants; bad SCB lifetime or partially initialized SCBs will surface as stale sense data or bad DMA addresses elsewhere.

## Test Signals

- Compile coverage from all AIC79xx translation units validates declarations and inline dependencies.
- Runtime signals include successful command completion with autosense, correct mode restoration around procfs SEEPROM writes, and no register access failures during PCI memory-mapped probing.
