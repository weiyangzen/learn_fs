# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo.c

Purpose: owns the global MicroBlaze CPU description, version/family lookup tables, CPU information setup, clock setup, and `/proc/cpuinfo` seq operations.

Important APIs and state: global `struct cpuinfo cpuinfo`; `setup_cpuinfo()` discovers the CPU node and chooses static/full-PVR population; `setup_cpuinfo_clk()` reads the CPU clock via CCF or `timebase-frequency`; `cpuinfo_op` prints hardware capabilities. Lookup tables translate MicroBlaze hardware-version and FPGA-family strings to numeric codes.

Control flow: setup chooses no-PVR, full-PVR, or fallback handling, warns if stream instructions are unprivileged, and releases the CPU OF node. Clock setup must run while `cpu` is still valid and BUGs if no frequency is found. `/proc/cpuinfo` iterates up to `NR_CPUS` but prints global single-CPU data.

State and persistence: `cpuinfo` persists for the lifetime of the kernel. The static `cpu` pointer is retained between CPU info and clock setup. No runtime mutation is expected after boot.

Dependencies and integration: used by setup, cache init, timer fallback, kgdb PVR export, and procfs. Depends on OF CPU nodes and optional clock provider.

Risks and test signals: the `cpu_has_pvr()` return semantics are subtle; comments and switch labels can be confusing. Missing CPU clock causes BUG. Test boot logs, `/proc/cpuinfo`, clock fallback, and systems with no/full/unsupported PVR.
