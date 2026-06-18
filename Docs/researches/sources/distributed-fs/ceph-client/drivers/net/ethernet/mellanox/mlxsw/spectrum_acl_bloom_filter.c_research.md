<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_bloom_filter.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_bloom_filter.c

## Purpose

`spectrum_acl_bloom_filter.c` maintains the A-TCAM Bloom filter used with ERP banks. It computes hardware-specific Bloom indexes from encoded ACL keys, ERP IDs, and region IDs, refcounts programmed bits per ERP bank, and writes `PEABFE` only on zero-to-one or one-to-zero transitions.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_bf` stores a mutex, per-bank size, and flexible array of refcounts for every ERP-bank/Bloom-index pair.
- Spectrum-2/3 helpers encode padded 23-byte chunks and hash them with CRC-16.
- Spectrum-4 helpers encode 20-byte chunks, shift packed chunks to account for 14-bit IDs, and combine CRC-10 row and CRC-6 column results.
- `mlxsw_sp_acl_bf_entry_add()` and `mlxsw_sp_acl_bf_entry_del()` update refcounts and write `PEABFE` records.
- `mlxsw_sp_acl_bf_init()` sizes the refcount array from `ACL_MAX_BF_LOG` and the ERP-bank count.
- `mlxsw_sp2_acl_bf_ops` and `mlxsw_sp4_acl_bf_ops` select chip-specific index calculation.

## Control Flow

For each A-TCAM entry, the selected `index_get()` implementation encodes only the chunks needed by the region key size. Each chunk combines key blocks, ERP id, and region id. Spectrum-2/3 hash the resulting byte stream with CRC-16. Spectrum-4 uses CRC-10 for row and CRC-6 for column, with chunk shifts for multi-chunk packed keys. Add locks the Bloom object, computes the rule-count index as `erp_bank * bank_size + bf_index`, increments an existing nonzero refcount if present, or writes an enable record to hardware and sets the refcount to one. Delete performs the inverse and writes a disable record only when the refcount reaches zero.

## State And Persistence

State is an in-memory refcount table protected by `bf->lock`, plus hardware Bloom bits in `PEABFE`. Refcounts are authoritative for avoiding premature bit clearing when multiple entries hash to the same index. Hardware state persists until deletion, region teardown, or device reset.

## Dependencies And Integration Points

The file is called from ERP/A-TCAM insertion and removal paths. It depends on region key metadata from AFK, A-TCAM encoded keys, ERP-bank mapping from `spectrum_acl_erp.c`, resource `ACL_MAX_BF_LOG`, and `PEABFE` register packing. Chip-specific ops are selected by the Spectrum family.

## Risks

- Hash/encoding layout is hardware-contract code; byte offsets, shifts, and padding errors cause lookup misses.
- Delete failure to allocate the `PEABFE` payload leaves a hardware bit set while software refcount reaches zero.
- Refcount underflow would corrupt Bloom state; callers must balance add/remove per ERP bank.
- Spectrum-4 chunk shifting writes into adjacent bytes by design, so buffer sizing and chunk-count assumptions matter.

## Test Signals

Validate Bloom index vectors against hardware/reference vectors for Spectrum-2/3/4, add/delete collision refcounting, multi-bank ERP use, all key sizes from one to three chunks, allocation failure on add/delete, and A-TCAM lookups before and after ERP rehash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_bloom_filter.c -->
