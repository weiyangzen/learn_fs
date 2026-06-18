<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-probe-vls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-probe-vls.c

Purpose: enumerates supported SVE vector lengths and validates that `PR_SVE_SET_VL` agrees with hardware `RDVL`.

Important APIs and functions: `main` uses `getauxval(AT_HWCAP)`, `prctl(PR_SVE_SET_VL)`, `rdvl_sve()`, and sigcontext helpers `sve_vl_valid`/`sve_vq_from_vl`.

Control flow: skip if SVE unsupported, iterate downward from `SVE_VQ_MAX`, set each candidate VL, mask returned flags, compare against `rdvl_sve`, validate the VL, store unique VQs, then report two kselftest passes and print supported VLs in ascending order.

State and persistence: stack/static VQ array only. No files.

Dependencies and integration: links with `rdvl.S` and uses kselftest output. It provides a capability/probing signal for other VL-dependent tests.

Risks: many iterations on implementations with unusual VL sets; exits fail on prctl or invalid VL rather than recording individual subtest failures.

Test signals: plan of 2; pass messages for enumeration and validity, followed by supported VL list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-probe-vls.c -->
