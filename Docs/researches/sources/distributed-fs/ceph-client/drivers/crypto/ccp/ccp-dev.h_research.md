# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev.h

## Purpose

`ccp-dev.h` is the internal device-layer contract for AMD CCP hardware. It defines register offsets, bit encodings, queue/storage constants, software device/queue/DMA structures, workarea abstractions used by operation conversion, generic `ccp_op` fields, v5 descriptor layout, helper address accessors, lifecycle prototypes, and version action tables.

## Important APIs, Types, And Functions

- Register constants cover generic, v3, and v5 queue/control/TRNG/interrupt/LSB registers.
- Storage constants define v3 KSB and v5 LSB dimensions, per-operation storage block counts, RSA/ECC/PASSTHRU sizes, and DMA pool limits.
- `struct ccp_dma_cmd`, `ccp_dma_desc`, and `ccp_dma_chan` model DMAengine provider state.
- `struct ccp_cmd_queue` models one hardware queue, including v5 ring memory, storage block assignments, IRQ state, kthread state, MMIO register pointers, and per-engine stats.
- `struct ccp_device` is the top-level device state: SP device, IO registers, command/backlog lists, queues, hwrng, DMAengine, storage block bitmaps, suspend state, axcache, stats, and debugfs.
- `struct ccp_dma_info`, `ccp_dm_workarea`, `ccp_sg_workarea`, `ccp_data`, and `ccp_mem` describe DMA buffers and workareas used by operation setup.
- `struct ccp_aes_op`, `ccp_xts_aes_op`, `ccp_des3_op`, `ccp_sha_op`, `ccp_rsa_op`, `ccp_passthru_op`, `ccp_ecc_op`, and `ccp_op` are normalized operation descriptions consumed by v3/v5 action tables.
- `struct ccp5_desc` and nested dword structs describe the v5 8-dword command descriptor.
- `struct ccp_actions` is the version-specific operation table.

## Control Flow

The header has no main control flow. It enables the generic scheduler to hold `struct ccp_cmd_queue` and `struct ccp_device`, the operation layer to build `struct ccp_op`, and v3/v5 files to implement the `ccp_actions` callbacks. Inline `ccp_addr_lo()` and `ccp_addr_hi()` convert DMA workarea addresses plus offsets into hardware command fields.

## State And Persistence Behavior

The definitions in this header describe nearly all persistent runtime CCP device state: command queues, lists, bitmaps, wait queues, kthreads, tasklets, DMA caches, hwrng state, suspend state, and debugfs handles. Hardware-visible descriptor and command state is represented by `ccp5_desc` and `ccp_op`.

## Dependencies And Integration Points

This header depends on Linux device, locking, list, wait, DMA, dmaengine, hwrng, interrupt, bitops, and SP-device definitions. It is included by generic device, v3/v5 device, debugfs, DMAengine, and operation conversion code.

## Risks And Edge Cases

- The macro `#define CCP_MEMTYPE_LSB CCP_MEMTYPE_KSB` references `CCP_MEMTYPE_KSB`, which is not an enum member in the visible code; this looks stale or typo-prone unless defined elsewhere before use.
- v5 descriptor bitfields assume compiler layout compatible with the hardware command format after explicit little-endian word conversion.
- Queue and device structures are cacheline-aligned in places; moving fields can affect contention.
- The header exposes many constants used across files; changing storage block sizes or register offsets has broad blast radius.

## Test Signals

Signals include full driver build across v3/v5/debugfs/DMAengine configs, sparse/endian checks for descriptors, operation tests for every engine, stress tests for storage block allocation, and ABI review against hardware documentation.
