# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/mb.c

Purpose: implements `/proc/cpuinfo` display for MicroBlaze by formatting the global `cpuinfo` hardware description into kernel seq-file output.

Important APIs and state: `show_cpuinfo()` formats FPGA family, CPU version, endian, MHz, BogoMips, hardware instruction units, MMU, multiplier/FPU revision, exception capabilities, stream-instruction privilege, cache configuration, hardware debug, PVR user fields, and page size. `cpuinfo_op` exposes seq start/next/stop/show callbacks.

Control flow: family/version strings are found by reverse lookup through the static tables. The iterator returns one logical entry per `NR_CPUS`, although the hardware data is global.

State and persistence: read-only reporting from `cpuinfo` and `loops_per_jiffy`. It does not allocate or mutate kernel state.

Dependencies and integration: procfs core consumes `cpuinfo_op`. It depends on `setup_cpuinfo()` and `setup_cpuinfo_clk()` having populated global state before userspace reads `/proc/cpuinfo`.

Risks and test signals: multi-CPU iteration can duplicate global values on configurations that expose more than one CPU. Unknown version/family codes fall back to "Unknown". Test `/proc/cpuinfo` output after DTS/PVR changes, especially cache policy and endian labels.
