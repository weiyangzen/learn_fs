<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/attr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/attr_test.c

Purpose: Tests sysfs PAPR energy/frequency attribute exposure and type correctness.

Important APIs and types: Defines `enum energy_freq_attrs`, `enum type`, `value_type`, `verify_energy_info`, and `main()`.

Control flow: `verify_energy_info()` walks expected sysfs attributes, determines whether each value should be string or numeric, reads files, and validates presence/format. `main()` runs it through the harness.

State and persistence: No state is modified; it only reads sysfs attribute files.

Dependencies and integration points: Depends on PAPR platform sysfs layout, `utils.h` file helpers, and the kselftest harness.

Risks: Sysfs availability is platform/firmware dependent. Format checks must track kernel ABI changes for new attributes.

Test signals: Pass means expected PAPR energy/frequency attributes are present and parseable on supported systems; unsupported systems should skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/attr_test.c -->
