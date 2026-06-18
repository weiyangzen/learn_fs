## sources/distributed-fs/ceph-client/lib/raid6/test/test.c

Purpose: standalone RAID-6 recovery correctness test. It exercises all available recovery algorithms against all available syndrome algorithms for a 16-disk stripe, including P and Q.

Important APIs/functions: `makedata()` fills data buffers and pointer table entries. `disk_type()` labels D/P/Q slots. `test_disks()` injects two failed disks, calls `raid6_dual_recov()`, and compares recovered buffers. `main()` iterates `raid6_recov_algos` and `raid6_algos`, then invokes `raid6_select_algo()` at the end.

Control flow: initial data is randomized. For each valid recovery backend, the program installs its `data2` and `datap` functions. For each valid syndrome backend, it regenerates P/Q, then tests every pair of failed disks. If the syndrome backend supports `xor_syndrome`, the test also simulates read-modify-write ranges by applying xor-syndrome before and after replacing a data range, then repeats failure-pair validation.

State and persistence: static aligned arrays hold original data, current pointer table, and recovery scratch pages. No persistent external state exists; output is printed to stdout and the process return code is nonzero on errors.

Dependencies/integration: depends on the userspace RAID-6 archive built by the Makefile and generic interfaces in `linux/raid/pq.h`.

Risks/test signals: the D+Q failure case is skipped because it is equivalent to RAID-5-style XOR plus Q recomputation and is not implemented as a direct scenario. Strong signal comes from exhaustive disk-pair checks across algorithm combinations and xor-syndrome RMW paths.
