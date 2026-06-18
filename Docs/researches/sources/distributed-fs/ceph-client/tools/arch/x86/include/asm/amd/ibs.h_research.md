# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/amd/ibs.h

## Purpose
AMD Instruction Based Sampling register-layout header for x86 tools.

## Important APIs, Types, and Functions
Defines IBS data source constants, unions `ibs_fetch_ctl`, `ibs_op_ctl`, `ibs_op_data`, `ibs_op_data2`, `ibs_op_data3`, `ic_ibs_extd_ctl`, and `struct perf_ibs_data` with raw caps/data and MSR register storage.

## Control Flow, State, and Persistence
No active control flow. Consumers read MSR snapshots into the unions and inspect bitfields for fetch/op sample validity, latency, cache/TLB misses, branch metadata, data source, and memory operation details.

## Dependencies and Integration Points
Depends on `../msr-index.h` for IBS MSR count constants. Integrated with perf AMD IBS decoding and sample export paths.

## Risks and Test Signals
Risks include C bitfield layout/endian assumptions, family/model-specific field changes, and reserved-bit interpretation. Test signals are perf IBS decode tests with known MSR values and build checks against current MSR index definitions.
