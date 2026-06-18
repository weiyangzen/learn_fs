# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_mpeg2.c

Purpose: MPEG1/2 stateless decode backend for Cedrus, programming MPEG engine registers from MPEG2 sequence/picture/quantisation controls and exporting `cedrus_dec_ops_mpeg2`.

Important APIs/functions: IRQ helpers inspect `VE_DEC_MPEG_STATUS`, clear status, and disable IRQ bits. `cedrus_mpeg2_setup()` enables the MPEG engine, writes intra and non-intra quant matrices, packs MPEG picture header flags/F-codes, programs coded/bound dimensions, writes forward/backward reference buffer addresses from timestamps, writes destination addresses, source bitstream length/address/end, resets macroblock/error tracking, and enables finish/error/data-request IRQs. `cedrus_mpeg2_trigger()` starts hardware MPEG VLD/MPEG2 decode at macroblock boundary.

Control flow: each MPEG2 job configures all registers in setup, then trigger starts decode. The common IRQ handler maps backend status to buffer done/error.

State and persistence: no codec-private persistent allocations; state is per-job register programming and capture reference buffers located by timestamp.

Dependencies/integration: consumes V4L2 MPEG2 stateless controls, vb2 DMA-contig source/capture buffers, and common Cedrus engine/address helpers.

Risks: quantisation control is assumed present. Reference timestamp lookup can yield zero addresses. MPEG1 source pixfmt shares this backend through platform formats but trigger sets MPEG2 mode here; in this tree Cedrus exposes only `V4L2_PIX_FMT_MPEG2_SLICE` in `cedrus_video.c`.

Test signals: I/P/B MPEG2 slices, custom quant matrices, missing forward/backward references, min/max resolution, short payloads, and IRQ error/data-request paths.
