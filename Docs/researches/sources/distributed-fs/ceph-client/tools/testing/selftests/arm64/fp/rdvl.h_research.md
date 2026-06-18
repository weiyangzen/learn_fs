<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.h

Purpose: declaration header for assembly vector-length helper functions.

Important APIs: declares `int rdvl_sme(void);` and `int rdvl_sve(void);`.

Control flow and state: none.

Dependencies and integration: included by VL probing and syscfg tests that link against `rdvl.S`.

Risks: signature changes must stay in lockstep with assembly return convention and C callers.

Test signals: indirect through caller comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.h -->
