# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_bl.h

## Purpose
`qat_bl.h` defines QAT buffer-list descriptor formats and the conversion/free API used to present Linux scatterlists to QAT firmware.

## Important APIs, Types, And Functions
Key definitions are `QAT_MAX_BUFF_DESC`, `struct qat_alg_buf`, `struct qat_alg_buf_list`, `struct qat_alg_fixed_buf_list`, `struct qat_request_buffs`, and `struct qat_sgl_to_bufl_params`. It declares `qat_bl_free_bufl()` and `qat_bl_sgl_to_bufl()`. The inline `qat_algs_alloc_flags()` maps Crypto API request flags to `GFP_KERNEL` or `GFP_ATOMIC`.

## Control Flow
No executable flow beyond `qat_algs_alloc_flags()` exists here. Callers allocate request context containing `qat_request_buffs`, call `qat_bl_sgl_to_bufl()` before firmware submission, pass `blp`/`bloutp` into firmware requests, and call `qat_bl_free_bufl()` on completion or immediate submission failure.

## State And Persistence Behavior
`qat_request_buffs` tracks per-request descriptor pointers, DMA addresses, sizes, inline fixed-list storage, and inline/dynamic ownership flags. Descriptor lists are packed and fixed descriptors are 64-byte aligned for hardware consumption.

## Dependencies And Integration Points
The header includes Crypto API request flags, scatterlists, and Linux types. It is shared by symmetric crypto and compression code.

## Risks
Structure packing and the `static_assert()` around the header group protect firmware ABI layout. Adding fields outside the grouped header would break `qat_alg_fixed_buf_list` assumptions. `QAT_MAX_BUFF_DESC` controls inline versus dynamic allocation and affects atomic allocation pressure.

## Test Signals
Compile-time static assert verifies layout. Runtime tests with small and large SGL counts validate inline/dynamic paths and allocation flags for sleepable and atomic requests.
