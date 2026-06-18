<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-util.h

Purpose: shared GCS UAPI and inline-instruction helper header.

Important definitions and functions: syscall/regset constants `__NR_map_shadow_stack`, `NT_ARM_GCS`; prctl operations and mode bits; token flags and cap token masks; `get_gcspr` reads `GCSPR_EL0`; `gcsss1`/`gcsss2` implement GCS stack-switch instructions; `chkfeat_gcs` executes CHKFEAT for GCS.

Control flow and state: inline helpers access architectural state but store nothing persistently.

Dependencies and integration: included by C GCS tests and bridges missing or new UAPI definitions until libc/kernel headers catch up.

Risks: fallback syscall numbers and constants must match the running kernel ABI. Encoded instructions require correct toolchain/CPU support.

Test signals: indirect; basic, libc, and locking tests validate helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-util.h -->
