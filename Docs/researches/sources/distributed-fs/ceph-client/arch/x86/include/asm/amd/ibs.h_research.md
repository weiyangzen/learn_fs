## `sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/ibs.h`

Purpose: defines AMD Instruction-Based Sampling MSR bitfield layouts, data source constants, and the perf IBS data buffer contract.

Important APIs and types: unions `ibs_fetch_ctl`, `ibs_op_ctl`, `ibs_op_data`, `ibs_op_data2`, `ibs_op_data3`, and `ic_ibs_extd_ctl` map IBS MSRs into named bitfields. Constants describe IBS data source and extended data source encodings. `struct perf_ibs_data` contains size/caps and captured IBS MSR values.

Control flow: no runtime logic; used by IBS perf driver code to program, decode, and export sampled fetch/op records.

State and persistence: structures mirror hardware MSR state at sample time. No state is stored by this header.

Dependencies and integration points: AMD IBS MSR indexes, perf sampling, CPU family documentation, and userspace perf decoding of IBS records.

Risks: bitfield layouts must match AMD PPR definitions exactly. Compiler bitfield ordering assumptions are tied to target ABI. Incorrect data-source constants mislabel memory hierarchy samples.

Test signals: IBS perf sampling on supported AMD CPUs, decode checks for fetch/op latency, branch/data source samples, and build tests across compilers/configs.
