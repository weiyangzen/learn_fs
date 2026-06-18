# sources/distributed-fs/ceph-client/drivers/edac/amd64_edac.h Research

## Purpose
This header defines the private data model, register constants, and helper interfaces used by the AMD64 EDAC driver. It captures AMD DCT, UMC, chip-select, DRAM range, error injection, ECC settings, and per-family operation abstractions.

## Important APIs, Types, and Functions
Important constants include AMD PCI device IDs, DCT/DRAM range registers, chip-select base/mask offsets, North Bridge ECC capability bits, scrub and injection registers, UMC channel offsets, and UMC ECC capability bits. Core structures are `struct error_injection`, `struct reg_pair`, `struct dram_range`, `struct chip_select`, `struct amd64_umc`, `struct amd64_family_flags`, `struct amd64_pvt`, `struct err_info`, `struct ecc_settings`, and `struct low_ops`. Inline helpers include `get_umc_base()`, `get_dram_base()`, `get_dram_limit()`, `extract_syndrome()`, `dct_sel_interleave_addr()`, cache-disable/enable helpers for injection, `dram_intlv_en()`, `dhar_valid()`, and `dct_sel_baseaddr()`. It declares the PCI config access wrappers implemented in `amd64_edac.c`.

## Control Flow
The header itself has no runtime control flow. Its `low_ops` callback table defines how the C file dispatches family-specific behavior for sysaddr-to-csrow mapping, DBAM-to-chip-select sizing, hardware discovery, ECC enablement checks, MC attribute setup, register dumps, and MCE error-info extraction.

## State and Persistence
No state is allocated in the header. It defines the persistent per-node private state retained while each EDAC MC instance is registered. The fields mirror hardware registers and include mutable injection staging values and ECC restore bookkeeping.

## Dependencies and Integration Points
The header depends on Linux PCI, EDAC, bitfield, MSR, CPU-device, and AMD MCE headers. It is private to `amd64_edac.c` and integrates with `mce_amd.h`, AMD NB PCI enumeration, x86 topology, and EDAC MC structures.

## Risks and Edge Cases
The register constants encode many AMD family-specific layouts; incorrect reuse across family/model boundaries can corrupt decoding. `struct amd64_pvt` is large and central, so adding fields requires careful initialization and teardown. Inline helpers read PCI config in some cases, which means apparent pure calculations can fail or depend on hardware access.

## Test Signals
Compile coverage with `amd64_edac.c` is the first signal. Runtime validation should compare decoded DRAM ranges, chip-select sizes, UMC register snapshots, syndrome extraction, and injection attributes against hardware documentation on representative AMD families. Static review should focus on whether new family/model logic updates both this header and `per_family_init()` consistently.
