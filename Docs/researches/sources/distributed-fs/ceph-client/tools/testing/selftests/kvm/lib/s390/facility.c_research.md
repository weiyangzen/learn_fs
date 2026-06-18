# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/facility.c

## Purpose
This file defines global storage for s390 facility-test state shared by the facility helpers and tests.

## Important APIs, Types, and Functions
It defines `u64 stfl_doublewords[NB_STFL_DOUBLEWORDS]` and `bool stfle_flag`. There are no functions.

## Control Flow
There is no executable control flow. Other compilation units read or populate these globals to represent Store Facility List data and whether extended facility-list behavior is active.

## State, Dependencies, and Integration
The globals are persistent process state and depend on declarations/constants from `facility.h`. This file exists to provide exactly one definition for link-time storage.

## Risks and Test Signals
Risks are ordinary global-state hazards: tests must initialize or refresh these fields before relying on them. Link failures catch missing or duplicate definitions; semantic issues show up in facility-dependent tests.
