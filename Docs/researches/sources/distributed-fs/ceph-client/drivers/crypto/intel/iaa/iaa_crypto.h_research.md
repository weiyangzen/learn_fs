# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto.h Research

## Purpose
`iaa_crypto.h` is the shared internal header for the Intel IAA crypto compression driver. It defines hardware operation flags, completion constants, compression-mode limits, fixed-deflate metadata, workqueue/device state structures, AECS table layout, compression mode registration APIs, and per-transform Crypto API context.

## Important APIs, Types, and Functions
Important constants include IAA decompress flags (`IAA_DECOMP_ENABLE`, `IAA_DECOMP_FLUSH_OUTPUT`, `IAA_DECOMP_CHECK_FOR_EOB`, `IAA_DECOMP_STOP_ON_EOB`, `IAA_DECOMP_SUPPRESS_OUTPUT`), compress flags (`IAA_COMP_FLUSH_OUTPUT`, `IAA_COMP_APPEND_EOB`), `IAA_COMPLETION_TIMEOUT`, known error/status codes, `IAA_COMP_MODES_MAX`, fixed header constants, and aggregate `IAA_COMP_FLAGS`/`IAA_DECOMP_FLAGS`.

`struct iaa_wq` represents an IDXD workqueue bound to crypto. It tracks list membership, the underlying `idxd_wq`, reference count, remove flag, parent `iaa_device`, and optional stats counters. `struct iaa_device` groups IDXD device state, per-mode DMA tables, workqueue list/count, and optional stats counters. `struct wq_table_entry` is the per-CPU workqueue selection table.

`struct aecs_comp_table_record` models the IAA Analytics Engine Configuration and State compression table, including CRC/checksum fields, output accumulator, literal/length symbols, and distance symbols. `struct iaa_compression_mode` stores global mode definition tables plus optional per-device init/free hooks. `struct iaa_device_compression_mode` stores per-device DMA-coherent AECS state.

The exported APIs are `iaa_aecs_init_fixed()`, `iaa_aecs_cleanup_fixed()`, `add_iaa_compression_mode()`, and `remove_iaa_compression_mode()`. `struct iaa_compression_ctx` is the Crypto API transform context, containing compression mode, verification setting, async mode, and interrupt mode. The header also declares global `iaa_devices` and `iaa_devices_lock`.

## Control Flow
`iaa_crypto_comp_fixed.c` registers a global fixed compression mode through `add_iaa_compression_mode()`. `iaa_crypto_main.c` copies those mode tables into per-device DMA AECS tables when IDXD workqueues probe, uses `iaa_compression_ctx` during acomp operations, and references `iaa_wq`/`iaa_device` to select hardware resources.

## State and Persistence
The header defines only in-memory kernel state. Global compression modes persist while the module is loaded; per-device modes persist while IAA devices/workqueues are bound; per-transform contexts persist while a Crypto API transform exists.

## Dependencies and Integration Points
It depends on Linux Crypto API headers, IDXD core and UAPI headers, list/mutex users in the C files, and hardware descriptor definitions from IDXD. It is the contract between the fixed-mode table file, main IAA driver, and stats code.

## Risks and Edge Cases
`IAA_COMP_MODES_MAX` is only two, so new modes can fail registration if slots are exhausted. `struct aecs_comp_table_record` is packed and hardware-facing; layout or alignment changes can break DMA programming. Reference and remove fields in `iaa_wq` are central to hot-remove safety. Optional stats fields are present in structures regardless of stats object linkage, so update functions must be valid in both configurations.

## Test Signals
Compile tests should cover stats on/off. Runtime tests should validate mode registration/removal ordering, per-device AECS DMA allocation, hot-remove with active references, and fixed mode availability in the acomp `deflate` algorithm.
