<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.S

Purpose: assembly implementation of two vector-length readers used by C selftests.

Important APIs and symbols: exports `rdvl_sve` and `rdvl_sme`. `rdvl_sve` executes `rdvl x0, #1`; `rdvl_sme` executes encoded `rdsvl 0, 1`. Both start with BTI-compatible `hint 34` and return VL in x0.

Control flow and state: straight-line leaf functions with no storage.

Dependencies and integration: includes `sme-inst.h`, requires SVE/SME instruction support as appropriate, and is linked with `rdvl-sve`, `rdvl-sme`, `sve-probe-vls`, and `vec-syscfg`.

Risks: callers must feature-gate execution. Incorrect assembler encoding for `rdsvl` would affect every SME VL validation.

Test signals: return value must match `prctl(...SET_VL)` and procfs default VL expectations in caller tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.S -->
