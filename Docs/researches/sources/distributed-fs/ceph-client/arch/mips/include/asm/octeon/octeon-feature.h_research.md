# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon-feature.h

Purpose: centralizes OCTEON feature detection by mapping model families and selected fuse registers to named hardware capabilities.

Important APIs/types/functions: `enum octeon_feature` lists capabilities such as PKND, CN68XX WQE layout, SAAD atomics, ZIP, dormant crypto, PCIe, SRIO, Interlaken, key memory, LED controller, trace buffer, management port, RAID, USB, no-WQE IPD mode, DFA, MDIO clause 45, NPEI, HFA, DFM, CIU2/CIU3, FPA3, and FAU. `enum octeon_feature_bits` includes `OCTEON_HAS_CRYPTO`, backed by external `__octeon_feature_bits`. `octeon_has_crypto()` checks that cached bit. `octeon_has_feature()` is a switch-based inline model/fuse probe.

Control flow: `octeon_has_feature` uses `OCTEON_IS_MODEL` predicates for most capabilities. Dormant crypto additionally reads `CVMX_MIO_FUS_DAT2` and checks fuse fields. Defaults return false for unknown features.

State and persistence: no state is stored except the external `__octeon_feature_bits` cache for crypto. Feature decisions reflect processor ID and immutable fuses at runtime.

Dependencies and integration points: includes `cvmx-mio-defs.h` and `cvmx-rnm-defs.h`; relies on model macros and CSR access from `octeon-model.h`/`cvmx.h`. WQE accessors, PCIe/SRIO/USB setup, interrupt-controller selection, and crypto paths use these probes.

Risks: the function is intended for constant feature arguments so compilers can optimize the switch; nonconstant use is slower. Model tables must stay aligned with hardware support. Fuse reads must be valid on checked families. Incorrect feature answers select wrong WQE layouts, interrupt controllers, or unavailable devices.

Test signals: model-matrix tests should verify each feature against known CN3XXX/CN5XXX/CN6XXX/CN7XXX hardware. Crypto tests should compare `octeon_has_crypto` cached bits with fuse-derived capabilities.
