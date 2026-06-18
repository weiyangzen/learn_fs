<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_test.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_test.c

Purpose: Provides KUnit coverage for PowerVR GPU ID string decoding.

Important APIs/types/functions: Defines the KUnit case `decode_gpuid_string`, suite `pvr_tests_suite`, and uses `pvr_gpuid_decode_string()`, `pvr_gpu_id_to_packed_bvnc()`, and `PVR_PACKED_BVNC()`.

Control flow: The test initializes a sentinel bad GPU ID, runs valid decode cases, then invalid cases for empty input, nonnumeric parts, overlong strings, overflow, and wrong dot/part counts. Invalid cases verify the output structure remains unchanged.

State and persistence behavior: No persistent state. The test uses stack-local structs and KUnit expectations.

Dependencies: Includes `pvr_device.h`, KUnit, visibility helpers, errno/string/types, and imports the exported-for-KUnit namespace.

Integration points: Runs as the PowerVR driver's in-kernel unit test suite named `pvr_tests`.

Risks: Coverage is intentionally narrow and does not exercise VM, sync, stream, or hardware paths. If GPU ID parsing behavior changes, tests must be updated to preserve output-on-error semantics.

Test signals: KUnit pass/fail for valid BVNC strings and malformed inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_test.c -->
