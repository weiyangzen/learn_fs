# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/Makefile

## Purpose
Registers EEH shell selftests and helper scripts with kselftest.

## Important APIs, Types, and Functions
`TEST_PROGS` lists `eeh-basic.sh`, `eeh-vf-aware.sh`, and `eeh-vf-unaware.sh`; `TEST_FILES := eeh-functions.sh`; includes `../../lib.mk`.

## Control Flow
No custom logic; kselftest handles install and execution.

## State and Persistence
No state here; runtime state is in sysfs/debugfs during shell tests.

## Dependencies and Integration Points
Integrates EEH recovery tests into the PowerPC selftest suite.

## Risks and Test Signals
Risk is high runtime impact from EEH injection, but this Makefile only exposes the scripts. Successful install must include the helper.
