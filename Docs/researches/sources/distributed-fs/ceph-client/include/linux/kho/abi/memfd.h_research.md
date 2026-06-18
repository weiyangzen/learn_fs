# sources/distributed-fs/ceph-client/include/linux/kho/abi/memfd.h

## Purpose

`memfd.h` defines the memfd Live Update ABI for serializing memfd file state across kexec through LUO and KHO. It preserves file position, size, seals, flags, folio state, and a KHO vmalloc descriptor for the folio array. The source was read as a complete 93-line file.

## Important APIs, Types, and Functions

Constants include `MEMFD_LUO_FOLIO_DIRTY`, `MEMFD_LUO_FOLIO_UPTODATE`, `MEMFD_LUO_ALL_SEALS`, and `MEMFD_LUO_FH_COMPATIBLE`. Types include packed `struct memfd_luo_folio_ser` with bitfield `pfn:52`, `flags:12`, and `index`, and packed `struct memfd_luo_ser` with `pos`, `size`, `seals`, `flags`, `nr_folios`, and `struct kho_vmalloc folios`.

## Control Flow

The old kernel serializes each relevant folio, stores the array through KHO vmalloc preservation, and hands the top-level `memfd_luo_ser` to the LUO file handler. The new kernel validates the compatible string and reconstructs the shmem/memfd file from folio PFNs and state flags.

## State and Persistence Behavior

The serialized file state persists across kexec. Seal bits are UAPI values; unsupported new seals require updating `MEMFD_LUO_ALL_SEALS` and bumping the compatible string.

## Dependencies and Integration Points

It depends on `linux/types.h`, KHO vmalloc ABI, file seal constants, LUO file handlers, and shmem/memfd internals.

## Risks and Edge Cases

The 52-bit PFN and 12-bit flags layout is packed ABI. Non-dirty but uptodate folios need correct zeroing semantics during restore. Unknown seal or flag bits must be rejected or masked by versioned rules.

## Test Signals

Memfd LUO restore tests with dirty, clean, fallocated, sealed, sparse, and large files; folio index ordering tests; unsupported seal tests; and compatible-string validation are relevant.
