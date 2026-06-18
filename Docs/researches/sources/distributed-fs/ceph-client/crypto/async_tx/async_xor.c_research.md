<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_xor.c -->
# sources/distributed-fs/ceph-client/crypto/async_tx/async_xor.c

## Purpose

`async_xor.c` implements the async_tx XOR and XOR-validation API used by RAID/parity code. It tries to offload page XOR work to a DMA engine and falls back to synchronous CPU XOR when no suitable channel, descriptor, alignment, or conversion storage is available.

## Important APIs, Types, and Flow

The exported APIs are `async_xor_offs()`, `async_xor()`, and `async_xor_val_offs()`. `async_xor_offs()` finds a `DMA_XOR` channel, allocates `dmaengine_unmap_data`, maps source pages as `DMA_TO_DEVICE`, maps the destination as bidirectional, and calls `do_async_xor()`. `do_async_xor()` splits operations by `device->max_xor`, chains partial descriptors through `submit->depend_tx`, clears callbacks for intermediate descriptors, and uses `DMA_PREP_INTERRUPT`/`DMA_PREP_FENCE` from submit flags. If descriptor allocation stalls, it quiesces dependencies and spins while issuing pending DMA.

The synchronous path uses `do_sync_xor_offs()`, converts source pages to virtual addresses with optional per-source offsets, optionally zeroes the destination for `ASYNC_TX_XOR_ZERO_DST`, then calls `xor_gen()`. `async_xor_val_offs()` similarly prefers `DMA_XOR_VAL`, otherwise performs an XOR into the destination and checks whether the destination page range is zero.

## State, Dependencies, and Integration

State is entirely per-call: mapped DMA addresses, submit control, dependency descriptors, and the caller-provided result flag. It depends on the DMA engine API, async_tx helpers, Linux pages, and RAID XOR helpers. The integration contract is subtle: in the synchronous path the destination is an implied XOR source unless `ASYNC_TX_XOR_DROP_DST` is set, while DMA only uses explicitly supplied source addresses.

## Risks and Test Signals

Risks center on source-list mutation, destination-as-source semantics, DMA alignment, descriptor starvation, and correct restoration of submit flags. Tests should cover DMA and synchronous fallback paths, differing source offsets, dropped destination source, zero-destination parity generation, multi-pass `max_xor` splitting, and validation result bits for zero and nonzero sums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_xor.c -->
