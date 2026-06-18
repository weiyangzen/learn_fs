# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/Makefile

## Purpose
Builds DEXCR tests and helper utilities.

## Important APIs, Types, and Functions
Defines `TEST_GEN_PROGS := dexcr_test hashchk_test`, `TEST_GEN_FILES := lsdexcr chdexcr`, includes lib.mk and flags.mk, links each target with `dexcr.c`, and adds helper object dependencies.

## Control Flow
The Makefile compiles common DEXCR helper logic into both tests and standalone tools, then delegates run/install rules to kselftest.

## State and Persistence
Only build outputs are persisted.

## Dependencies and Integration Points
Integrates PR_PPC_DEXCR selftests into the PowerPC suite and builds user utilities for listing/changing DEXCR controls.

## Risks and Test Signals
Risk is stale target dependencies when adding helper functions. Successful build and test harness runs are the main signals.
