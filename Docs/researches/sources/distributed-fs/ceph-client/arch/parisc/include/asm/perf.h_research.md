# sources/distributed-fs/ceph-client/arch/parisc/include/asm/perf.h

Purpose: defines PA-RISC CPU performance-monitoring register layout and event selectors for low-level perf support.

Important APIs/types/functions: exports performance counter control/status constants, CPU event encodings, and helper declarations used by perf and platform code.

Control flow: perf setup programs counter selectors, enables counting, handles overflow interrupts, and reads counter values.

State and persistence: hardware performance counters and control registers persist until reprogrammed. Dependencies and integration: integrates with `perf_event`, interrupt handling, processor identification, and control-register accessors.

Risks and test signals: wrong event encodings produce misleading metrics or interrupt storms. Test with `perf stat`, overflow sampling, CPU model gating, and counter reset/readback checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
