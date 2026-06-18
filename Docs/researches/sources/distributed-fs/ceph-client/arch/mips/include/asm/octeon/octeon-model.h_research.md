# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon-model.h

Purpose: defines OCTEON processor model, family, pass/revision, and matching macros used throughout the OCTEON support code.

Important APIs/types/functions: constants define CN3XXX, CN5XXX, CN6XXX, CNF7XXX, and CN7XXX families plus specific model/pass IDs such as CN38XX, CN58XX, CN56XX, CN52XX, CN63XX, CN68XX, CN70XX, CN73XX, CN78XX, CNF71XX, and CNF75XX. Matching flags include ignore revision/minor revision, check submodel, match previous models, and match family groups. Core APIs/macros are `OCTEON_IS_MODEL`, `OCTEON_IS_COMMON_BINARY`, `OCTEON_IS_OCTEON1/PLUS/2/3`, `octeon_model_get_string`, and `cvmx_get_octeon_family`.

Control flow: `OCTEON_IS_MODEL(x)` calls `__octeon_is_model_runtime__`, which reads the processor ID via `cvmx_get_proc_id()` and applies the large `__OCTEON_IS_MODEL_COMPILE__` macro. The matcher handles old CN3XXX revision encoding, newer CN5XXX+ encoding, submodels, pass matching, and family group ranges.

State and persistence: no mutable state. It reads the processor ID register at runtime. `OCTEON_IS_COMMON_BINARY()` is fixed to true in this kernel header, forcing runtime matching rather than compile-time specialization.

Dependencies and integration points: forward-declares `cvmx_get_proc_id` and `cvmx_read_csr`, includes `octeon-feature.h` at the end, and underpins model-gated CSR offsets, WQE layouts, PCIe/USB/SRIO feature checks, and errata workarounds.

Risks: model constants are explicitly internal to this framework and may change; external code should use the macros only. The macro is complex and easy to break with parenthesis or mask edits. Use in preprocessor `#if` is documented as unsupported. Wrong pass matching can select incorrect register layouts or skip errata.

Test signals: unit-style tests can feed synthetic chip IDs into the compile matcher macro, while hardware boot logs should verify `octeon_model_get_string`, family detection, and feature-gated code paths for each supported model/pass.
