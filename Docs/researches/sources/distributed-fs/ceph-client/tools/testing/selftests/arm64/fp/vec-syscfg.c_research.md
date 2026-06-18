<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vec-syscfg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vec-syscfg.c

Purpose: system-configuration selftest for SVE and SME vector length controls via procfs defaults and prctl process controls.

Important APIs, types, and functions: `struct vec_data` captures per-vector-type metadata, including HWCAP, `rdvl` helper, prctl operations, and procfs default file. Key functions include `get_child_rdvl`, `file_read_integer`, `file_write_integer`, `proc_read_default`, `proc_write_min`, `proc_write_max`, `prctl_get`, `prctl_set_same`, `prctl_set`, `prctl_set_no_child`, `prctl_set_for_child`, `prctl_set_onexec`, `prctl_set_all_vqs`, and `change_sve_with_za`.

Control flow: main sets a plan for all per-type tests plus cross-type tests, skips unsupported vector types, and runs procfs/prctl checks in an order that establishes default/min/max values before inheritance and all-VQ tests. Cross-type `change_sve_with_za` runs only when both SVE and SME are present.

State and persistence: mutates `/proc/sys/abi/sve_default_vector_length` and `/proc/sys/abi/sme_default_vector_length` when run as root, then attempts to restore defaults. Spawns helper binaries `rdvl-sve` and `rdvl-sme` to observe exec-time VL behavior.

Dependencies and integration: depends on `rdvl.S`, helper binaries, kselftest, root privileges for write tests, HWCAP bits, and procfs ABI files.

Risks: procfs mutation affects system-wide defaults during the test; restoration paths are best-effort and can be skipped after some failures. `change_sve_with_za` has a TODO for verifying ZA preservation beyond surviving activity.

Test signals: TAP results distinguish default reads, min/max writes, prctl get/set/inherit/onexec/all-VQ behavior, and SVE changes while SME is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vec-syscfg.c -->
