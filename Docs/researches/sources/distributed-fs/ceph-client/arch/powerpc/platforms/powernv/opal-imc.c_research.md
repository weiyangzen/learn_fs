## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-imc.c

### Purpose
`opal-imc.c` discovers OPAL In-Memory Collection counter units on PowerNV, creates Linux IMC PMUs for nest/core/thread/trace domains, exposes nest control blocks through debugfs, and stops firmware counters during shutdown or kdump boot.

### Important APIs, Types, And Functions
Key functions are `imc_pmu_create()`, `imc_get_mem_addr_nest()`, `export_imc_mode_and_cmd()`, `disable_nest_pmu_counters()`, `disable_core_pmu_counters()`, `get_max_nest_dev()`, `opal_imc_counters_probe()`, and `opal_imc_counters_shutdown()`. It relies on `struct imc_pmu`, `struct imc_mem_info`, `init_imc_pmu()`, `unregister_thread_imc()`, and OPAL `opal_imc_counters_stop()`.

### Control Flow
The platform driver probes `ibm,opal-imc-counters`, scans compatible IMC unit nodes, maps each device-tree `type` to an IMC domain, creates a PMU, and tracks whether core/thread PMUs registered. Nest PMUs read chip IDs and base addresses from firmware properties, apply the counter offset, and build a `mem_info` array ending with a zero entry. The first nest PMU also creates debugfs files for `imc_mode_*` and `imc_cmd_*`. If thread IMC exists without core IMC, thread support is unregistered.

### State, Persistence, And Dependencies
The driver persists registered PMU objects, debugfs dentries, and nest counter virtual addresses for the boot lifetime. Firmware counter state persists outside Linux, so shutdown and kdump paths explicitly stop nest and core engines. Dependencies include Open Firmware properties, `arch_debugfs_dir`, CPU/node topology, endian conversion for control words, and the shared IMC PMU layer.

### Integration Points
It is a built-in platform driver and is instantiated by `opal.c` via `opal_imc_init_dev()`. PMU registration feeds the perf IMC subsystem, while debugfs gives privileged operators direct control over nest mode/command words.

### Risks
The debugfs helpers use `debugfs_create_file_unsafe()` over firmware-shared memory, so invalid writes can perturb counters. Nest memory uses `phys_to_virt()` and assumes OPAL-provided memory is mapped. Error cleanup is partial, and shutdown explicitly notes that PMU unregister/memory cleanup is not handled.

### Test Signals
Useful checks include DT variants for each IMC type, missing `type`, `size`, `chip-id`, `base-addr`, and `offset` properties, kdump boot counter-stop behavior, debugfs read/write endian correctness, perf PMU registration, and shutdown stopping one counter per node/core sibling.
