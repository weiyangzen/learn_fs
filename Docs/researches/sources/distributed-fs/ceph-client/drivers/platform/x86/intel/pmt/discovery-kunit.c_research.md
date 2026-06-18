# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/discovery-kunit.c

Purpose: KUnit test module that exercises PMT feature discovery by querying available telemetry regions for every valid PMT feature ID.

Important APIs/types/functions: `validate_pmt_regions()` logs each region and asserts nonnegative platform metadata, nonzero GUID, and non-null/non-error mapped address. `test_intel_pmt_get_regions_by_feature()` iterates feature IDs from 1 through `FEATURE_MAX`, checks `pmt_feature_id_is_valid()`, calls `intel_pmt_get_regions_by_feature()`, validates available groups, and releases them with `intel_pmt_put_feature_group()`. `intel_pmt_discovery_test_suite` registers the single test case.

Control flow: when the KUnit module runs, it loops all known feature IDs. `-ENOENT` and other errors are warnings rather than hard failures, so the test is tolerant of hardware without a given feature. Available feature groups are validated structurally.

State and persistence: no persistent driver state. The test temporarily obtains feature groups whose references must be put after validation.

Dependencies and integration points: depends on KUnit, `linux/intel_pmt_features.h`, Intel VSEC, PMT discovery namespace, and exported discovery/telemetry feature group APIs. Imports `INTEL_PMT_DISCOVERY`.

Risks: many assertions are weak because fields are unsigned and `>= 0` is tautological; the strongest checks are GUID nonzero and address validity. The test warns rather than fails when no feature groups are available, making it more of a smoke/integration test than a strict unit test. It depends on real registered PMT regions unless a test harness supplies them.

Test signals: KUnit output should list available features and regions. A regression in feature group lookup, GUID population, or address mapping should show errors or assertion failures. Systems without PMT regions produce warnings but not necessarily failure.
