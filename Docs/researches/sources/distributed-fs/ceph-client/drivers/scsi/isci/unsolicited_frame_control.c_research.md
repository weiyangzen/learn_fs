# sources/distributed-fs/ceph-client/drivers/scsi/isci/unsolicited_frame_control.c

Purpose: manages ISCI unsolicited-frame DMA memory layout and release ordering for frames delivered by the SCU hardware outside normal request context.

Important APIs and functions: `sci_unsolicited_frame_control_construct()` lays out frame buffers, header table, and address table inside `ihost->ufi_buf`/`ihost->ufi_dma`. `sci_unsolicited_frame_control_get_header()` and `_get_buffer()` validate frame indices and return header data or payload buffer pointers. `sci_unsolicited_frame_control_release_frame()` marks a frame released and advances the software get pointer only when all earlier frames are releasable.

Control flow: construction starts buffers at the beginning of the UFI region, headers after `SCI_UFI_BUF_SIZE`, address table after `SCI_UFI_HDR_SIZE`, then fills `SCU_MAX_UNSOLICITED_FRAMES` entries with consecutive 1 KiB DMA buffers. Release computes ring index and cycle from `uf_control->get`, skips null address-table slots, rejects invalid indices, marks the target released, and only advances contiguous released entries to empty before writing an enabled get pointer value.

State and persistence: state is volatile in `sci_unsolicited_frame_control`: `get`, address-table entries, per-frame `state`, and virtual/physical table pointers. Hardware consumes the DMA addresses and get pointer. No disk persistence.

Dependencies and integration: depends on ISCI host allocation of UFI memory, SCU register bit macros, DMA address sizing, and controller code that writes `uf_control->get` to hardware after release.

Risks and test signals: the release loop is sensitive to ring off-by-one behavior and null table assumptions; a bad last null entry triggers `BUG_ON`. Tests should exercise in-order release, out-of-order release, invalid indices, all frames wrapping the cycle bit, and address/header alignment. Hardware bring-up should confirm no unsolicited-frame starvation after partial release.
