## sources/distributed-fs/ceph-client/arch/arm64/kernel/smp_spin_table.c

### Purpose
`smp_spin_table.c` implements the legacy spin-table CPU enable method for ARM64 systems whose secondary CPUs poll a release address instead of using PSCI.

### Important APIs, Types, And Functions
The file defines `secondary_holding_pen_release`, `cpu_release_addr[]`, helpers `write_pen_release`, `smp_spin_table_cpu_init`, `smp_spin_table_cpu_prepare`, `smp_spin_table_cpu_boot`, and the exported `smp_spin_table_ops` `cpu_operations` structure.

### Control Flow
`cpu_init` reads each CPU node's `cpu-release-addr`. `cpu_prepare` maps that address as normal cached memory, writes the physical address of `secondary_holding_pen` in little-endian form, cleans/invalidates the cache line, sends `sev`, and unmaps it. `cpu_boot` writes the target MPIDR into the holding-pen release variable and sends another `sev` so the secondary can leave its polling loop.

### State, Persistence, And Dependencies
Persistent state is the firmware-provided release address array and the `.mmuoff.data.read` holding-pen release word. Cache maintenance is part of the state contract because secondaries may be outside coherency while polling.

### Integration Points
The operations are selected by the CPU enable-method parser and then called by `smp.c`. It depends on DT CPU nodes, `secondary_holding_pen` assembly, physical address translation, I/O remapping, cache maintenance, and ARM `sev` events.

### Risks
Bad or missing `cpu-release-addr` prevents boot. Endianness, cacheability, or missing cache maintenance can strand CPUs. Spin-table platforms often lack reliable hot-unplug `cpu_die`, which feeds into `cpus_are_stuck_in_kernel` risk handling.

### Test Signals
Boot spin-table device-tree systems, test secondary bring-up under cold and warm reset, validate release-address endianness, and run cache-coherency-sensitive CPU online/offline or reboot tests.
