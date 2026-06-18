# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_debugdump.c

## Purpose

`nfp_net_debugdump.c` implements TLV-driven ethtool firmware/debug dumps for NFP PF devices. It loads a firmware dump specification from the `_abi_dump_spec` runtime symbol, calculates the dump size for a requested dump level, and populates an ethtool dump buffer with firmware name, hwinfo, selected hwinfo fields, runtime symbols, direct CSR ranges, XPB CSR ranges, ME CSR ranges, and indirect ME CSR contexts.

## Important APIs, Types, and Functions

External entry points are `nfp_net_dump_load_dumpspec()`, `nfp_net_dump_calculate_size()`, and `nfp_net_dump_populate_buffer()`. Key local types are `struct nfp_dump_tl`, `struct nfp_dumpspec_csr`, `struct nfp_dumpspec_rtsym`, `struct nfp_dump_csr`, `struct nfp_dump_rtsym`, `struct nfp_dump_prolog`, `struct nfp_dump_error`, `struct nfp_level_size`, and `struct nfp_dump_state`. Core helpers include `nfp_traverse_tlvs()`, `nfp_add_tlv_size()`, `nfp_dump_for_tlv()`, `nfp_dump_csr_range()`, `nfp_dump_indirect_csr_range()`, `nfp_dump_single_rtsym()`, `nfp_dump_hwinfo()`, and `nfp_dump_hwinfo_field()`.

## Control Flow

Dump spec loading looks up `_abi_dump_spec`, allocates a `struct nfp_dumpspec` with `vmalloc()`, and reads the runtime symbol into memory. Size calculation seeds the total with a prolog TLV, traverses top-level dump-level TLVs, selects the requested level, and recursively adds the aligned output size for each dumpable TLV. Population mirrors that traversal: write a prolog, find matching dump-level TLVs, dispatch each dumpable by type, reserve an aligned output TLV, then fill it from NFP CPP reads, XPB reads, runtime symbol reads, hwinfo strings, or error TLVs.

## State and Persistence Behavior

The file does not persist driver settings, but it reads persistent firmware/runtime state through CPP, XPB, RTSYM, MIP, and hwinfo interfaces. `struct ethtool_dump.len` is updated with the actual dumped size. Error conditions are embedded in output TLVs so a partial dump can still be returned with per-object failure metadata.

## Dependencies and Integration Points

It integrates with ethtool dump ops in `nfp_net_ethtool.c`, PF state in `struct nfp_pf`, runtime symbols from `nfp_rtsym`, hwinfo from `nfpcore/nfp.h`, MIP firmware names, NFP CPP read APIs, XPB reads, and indirect CSR helpers from `nfp_asm.h`. The output format is firmware ABI data and must remain deterministic for support tooling.

## Risks and Edge Cases

The TLV walker validates length and 4-byte alignment, but malformed firmware specs can still cause missing or error TLVs. Buffer accounting in `nfp_add_tlv()` is critical because ethtool provides the destination length. CSR specs are accepted only for 32- or 64-bit register widths. Runtime symbols and hwinfo keys must be NUL-terminated inside the TLV payload. Indirect CSR reads write context selector state before reads, so failures must preserve useful `error_offset` data.

## Test Signals

Tests should cover dump levels with valid CSR, indirect CSR, XPB, RTSYM, hwinfo, firmware-name, unknown, malformed-length, and missing-symbol TLVs. Fault injection around `nfp_cpp_read()`, `nfp_xpb_readl()`, `nfp_rtsym_read()`, and undersized ethtool buffers should verify error TLV creation and size consistency.
