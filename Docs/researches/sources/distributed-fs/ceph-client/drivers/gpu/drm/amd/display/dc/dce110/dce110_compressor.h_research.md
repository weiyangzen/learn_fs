# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.h

Purpose: declares the DCE110 compressor concrete object and FBC/LPT-related API surface.

Important types and APIs: `struct dce110_compressor` embeds the generic `struct compressor` and stores current DCP/DMIF register offsets in `struct dce110_compressor_reg_offsets`. `TO_DCE110_COMPRESSOR()` converts generic compressor pointers. Lifecycle APIs are `dce110_compressor_create()`, `dce110_compressor_construct()`, and `dce110_compressor_destroy()`. FBC APIs include power up, enable, disable, invalidation triggers, compressed surface address/pitch, and hardware-state query. LPT prototypes are declared as well.

Control flow role: the header lets resource code allocate and use the DCE110 implementation through generic compressor callbacks while still exposing specific helpers for FBC programming.

State and persistence: persistent software state is inherited from `struct compressor` plus current register offsets. Hardware FBC state persists outside the object.

Dependencies and integration: includes `../inc/compressor.h`, which supplies generic compressor fields, address/pitch params, and compression ratio/controller types. It integrates with the DCE110 Makefile and compressor function table in the C file.

Risks and test signals: LPT functions are declared but not implemented in the read implementation, so callers must rely on linked objects or avoid those symbols. Offset state must be refreshed before per-pipe register access. Compile/link tests should catch unused or missing LPT definitions; runtime tests should cover create/construct/destroy and FBC helper compatibility with the generic compressor interface.
