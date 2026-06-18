# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c

## Purpose
Provides a focused SDMA v4.4 RAS implementation shared by the broader SDMA v4.0 driver for IP version 4.4.0-class hardware. It maps SDMA instance register offsets, decodes EDC counter fields, reports RAS error counts, and clears hardware counters.

## APIs, Types, And Functions
The exported object is `struct amdgpu_sdma_ras sdma_v4_4_ras`. Internal data includes `sdma_v4_4_ras_fields`, a table of named single-error-detection fields across `regSDMA0_EDC_COUNTER` and `regSDMA0_EDC_COUNTER2`. Key helpers are `sdma_v4_4_get_reg_offset()`, `sdma_v4_4_get_ras_error_count()`, per-instance query/reset functions, aggregate query/reset functions, and `sdma_v4_4_ras_hw_ops`.

## Control Flow
RAS query iterates every SDMA instance, reads the two EDC counter registers through a helper that converts instance number to the correct register base, decodes nonzero field counts, logs detected fields, and accumulates counts into `ras_err_data`. Reset checks SDMA RAS support and writes zero to both EDC counter registers for each instance. The exported RAS block supplies these operations to the common AMDGPU SDMA RAS layer.

## State And Persistence
The file does not own long-lived software state beyond static tables and the exported `sdma_v4_4_ras` descriptor. Hardware EDC counters are the persistent state being queried and reset. Counts are folded into caller-provided `ras_err_data`; the file sets CE count to zero and accumulates SDMA single-error-detection counts as UE count according to the implementation comments.

## Dependencies And Integration
Depends on AMDGPU core definitions, SoC15 register access, SDMA 4.4.0 register masks, and AMDGPU RAS types. It is selected by `sdma_v4_0_set_ras_funcs()` for IP version 4.4.0, which makes this file an extension of the v4.0 SDMA implementation rather than a standalone IP block.

## Risks And Test Signals
Risks include hard-coded register offsets for up to five instances, any mismatch between field table masks and actual IP revision, and the unusual classification of single-error-detection counts into UE rather than CE. The field named for `SDMA_MC_RDRET_BUF_SED` uses the `SDMA_MC_WR_ADDR_FIFO_SED` field macro, which is worth auditing against hardware headers. Test signals include injected or harvested EDC counter values, correct per-instance logging, successful zeroing of counters, and no register-offset failures on all supported instance counts.
