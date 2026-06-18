## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.h

Purpose: public DCE112 compressor type and API declarations for FBC/LPT support.

Important types and APIs: `struct dce112_compressor_reg_offsets`, `struct dce112_compressor`, `TO_DCE112_COMPRESSOR`, lifecycle functions, FBC functions, LPT functions, and hardware state query helpers. It embeds the generic `struct compressor` from `../inc/compressor.h`.

Integration: callers allocate or receive a generic `struct compressor` and use these functions when the ASIC resource path selects the DCE112 implementation. Offset storage tracks the DCP/DMIF pipe currently attached to FBC.

Risks and test signals: API misuse can pass a generic compressor not created by this implementation into `TO_DCE112_COMPRESSOR`. Build tests catch signatures; runtime FBC/LPT tests verify object initialization, state queries, and destroy behavior.
