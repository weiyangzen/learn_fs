# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/hevc_regs.h

Purpose: this header defines register offsets and selected bit fields for the Meson HEVC-family decoder block used by VP9 and HEVC paths. It covers assist scratch/mailbox registers, parser/shift/CABAC controls, MPRED, MPP reference tables, decompression, DBLK, SAO, compressed-body/header, MMU, firmware CPU, IMEM DMA, and scaling controls.

Important constants: assist mailbox and scratch offsets begin around `0xc000`. Parser stream and command registers include `HEVC_STREAM_*`, `HEVC_SHIFT_*`, `HEVC_PARSER_*`, and parser interrupt controls. Motion prediction registers include `HEVC_MPRED_CTRL0` with bits for new picture/tile, TMVP, refs, and MV read/write. Reference table and canvas/decompression registers include `HEVCD_MPP_ANC2AXI_TBL_*`, `HEVCD_MPP_ANC_CANVAS_*`, and `HEVCD_MPP_DECOMP_CTL*`. SAO and compressed memory registers include `HEVC_SAO_*`, `HEVC_CM_BODY_*`, `HEVC_CM_HEADER_*`, and MMU header addresses.

Control flow and integration: `codec_vp9.c` uses these registers to program parser commands, workspace sub-buffer addresses, reference scaling, MCRCC, MPRED motion-vector buffers, SAO output addresses, compressed/FBC output, MMU maps, and decode start/status. `codec_hevc_common.c` uses decompression, MPP, SAO, and compressed-memory registers for shared buffer setup. `vdec_hevc.c` in the same module likely uses the same header for HEVC decode.

State and persistence behavior: values written through these offsets are live decoder hardware state. Assist scratch registers act as a firmware ABI. Reference, SAO, MPRED, and DBLK registers persist across frames until reprogrammed by codec frame setup or reset by hardware stop paths.

Dependencies: source files use `amvdec_read_dos()` and `amvdec_write_dos()` with these offsets against the DOS MMIO base. Bit macros depend on kernel `BIT()`.

Risks: many offsets are densely hardware-specific and shared across codecs; incorrect changes can break VP9 and HEVC simultaneously. Some register aliases overlap intentionally, such as DBLK status/config offsets, and should not be deduplicated without hardware confirmation. Revision-specific behavior is handled in codec code, not this header.

Test signals: VP9 and HEVC stream start, parser command load, mailbox IRQ, reference-table setup, 10-bit FBC/MMU decode, SAO output to NV12, and register traces comparing GXBB/GXL/G12A/SM1 behavior.
