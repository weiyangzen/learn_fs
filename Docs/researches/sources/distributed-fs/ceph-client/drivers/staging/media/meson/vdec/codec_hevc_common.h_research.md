# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_hevc_common.h

Purpose: this header defines the shared HEVC-family buffer-management and parser-command contract used by Meson VDEC codec implementations.

Important APIs and types: it defines parser skip configuration constants, `VDEC_HEVC_PARSER_CMD_LEN`, and the external `vdec_hevc_parser_cmd` array. `MAX_REF_PIC_NUM` is 24. `struct codec_hevc_common` stores per-reference FBC buffer virtual/physical addresses, per-reference MMU compressed-header buffers, and one MMU map buffer. Inline policy helpers decide whether a decode uses FBC, downsampling, or MMU based on capture pixel format, bit depth, and platform revision. Function declarations expose decode-head setup, FBC/MMU cleanup, buffer setup, and MMU map fill.

Control flow and integration: VP9 and HEVC implementations embed `struct codec_hevc_common` in their private session state, call setup during resume/source-change, call fill-map for frames on MMU-capable revisions, and call cleanup during stop. The inline helpers centralize format/revision policy so codec files do not duplicate those decisions.

State and persistence behavior: the header-defined struct owns DMA allocations that live across frames and must be released by the codec. `MAX_REF_PIC_NUM` bounds these arrays and must align with capture queue limits and hardware reference table capacity.

Dependencies: includes `vdec.h` for session/platform types and revision constants. The implementation also depends on HEVC register definitions and vb2 DMA helpers.

Risks: the simple inline policies currently treat all 10-bit decode as FBC/downsample and all G12A-or-newer FBC as MMU-backed, which may be too broad for future formats. Changing `MAX_REF_PIC_NUM` affects memory footprint and table programming loops.

Test signals: compile all codec users after any signature or policy change. Runtime tests should verify 8-bit versus 10-bit paths, revision gates, capture buffer counts near 24, and cleanup after setup failure.
