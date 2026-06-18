<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/processor.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/processor.c

### Purpose
`processor.c` discovers PA-RISC CPU devices, records boot and per-CPU metadata, enables FP support, publishes `/proc/cpuinfo`, and registers the CPU parisc bus driver.

### Important APIs, Types, And Functions
Globals include `boot_cpu_data`, `_parisc_requires_coherency`, and per-cpu `cpu_data`. Key functions are `processor_probe()`, `collect_boot_cpu_data()`, `init_per_cpu()`, `show_cpuinfo()`, and `processor_init()`.

### Control Flow
Boot collection queries PDC model, version, CPUID, capabilities, platform names, and serial data, feeding randomness and architecture descriptors. Device probing assigns logical CPU IDs, optionally reads PAT CPU/module information, fills `cpu_data`, stores topology, and adds secondary CPUs. `init_per_cpu()` sets firmware width, enables the FP coprocessor, records FP revision/model, initializes block TLB state, and panics on 64-bit kernels without FP.

### State, Persistence, And Dependencies
CPU identity and capabilities persist in `boot_cpu_data` and `cpu_data`. Dependencies include PDC/PAT firmware, parisc device inventory, topology, cache reporting, FP control registers, and SMP CPU registration.

### Integration Points
`setup.c` calls boot data collection and `processor_init()`, SMP startup calls `init_per_cpu()`, and procfs uses `show_cpuinfo()`.

### Risks
Probe ordering controls logical CPU numbering and topology. PAT firmware failures are treated as `BUG_ON()`. FP enablement is mandatory for 64-bit kernels and assumed by later kernel code.

### Test Signals
Validate boot logs, `/proc/cpuinfo`, secondary CPU discovery, PAT and legacy firmware paths, FP register availability, and topology output on SMP and UP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/processor.c -->
