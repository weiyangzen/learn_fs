# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-test.c

Purpose: KUnit tests for Arm SMMU v3 entry-writing and invalidation-set helpers. It verifies that STE/CD transitions use the expected number of sync points and remain hitless where required.

Important APIs, types, and functions: `struct arm_smmu_test_writer` wraps `arm_smmu_entry_writer`; `arm_smmu_v3_test_ste_expect_transition()` and `arm_smmu_v3_test_cd_expect_transition()` are the core assertions; helper constructors build bypass, abort, CD-table, S2, S1, SVA, release, and nested STE/CD shapes. `arm_smmu_v3_invs_test()` covers `arm_smmu_invs_alloc/merge/unref/purge`.

Control flow: each test builds an initial and target entry, runs `arm_smmu_write_entry()` through a fake writer, records every sync, checks that intermediate entries are equivalent to either old or new state for used bits during hitless transitions, checks whether an invalid entry was written, and verifies final memory equality. The suite initializes global bypass/abort STEs in `suite_init`.

State and persistence: all state is test-local except static fixtures (`bypass_ste`, `abort_ste`, fake `smmu`, fake `sva_mm`) and static invalidation examples. There is no hardware access; fake structures provide enough data for entry constructors.

Dependencies and integration points: depends on KUnit, `EXPORTED_FOR_KUNIT_TESTING` symbols from the SMMU v3 driver and SVA file, io-pgtable config structs, and SMMU entry helper APIs. Built only with `CONFIG_ARM_SMMU_V3_KUNIT_TEST`.

Risks: tests encode expected sync counts, so legitimate algorithm changes require deliberate test updates. Fake hardware data may not cover every implementation-specific bit. The invalidation tests are algorithmic and do not verify command queue hardware side effects.

Test signals: the suite itself is the primary signal: bypass/abort/CD-table/S2/S1/SVA/nested transitions, hitless versus non-hitless paths, stall and ATS variants, SVA release CD behavior, and invalidation merge/refcount/trash purge semantics.
