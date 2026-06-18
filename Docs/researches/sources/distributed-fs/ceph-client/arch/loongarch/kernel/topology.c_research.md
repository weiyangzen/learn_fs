## sources/distributed-fs/ceph-client/arch/loongarch/kernel/topology.c

### Purpose
`topology.c` supplies the LoongArch CPU hotplug policy hook for topology code. It marks I/O master CPUs as non-hotpluggable so platform-critical CPUs remain online.

### Important APIs, Types, And Functions
Under `CONFIG_HOTPLUG_CPU`, it defines `arch_cpu_is_hotpluggable(int cpu)` and calls `io_master(cpu)`.

### Control Flow
The function returns the negation of `io_master(cpu)`: normal CPUs are hotpluggable, I/O master CPUs are not.

### State, Persistence, And Dependencies
No local state is stored. It depends on `loongson_sysconf.cores_io_master` and related `io_master` logic populated during CPU/platform setup.

### Integration Points
Generic CPU hotplug and sysfs topology code call this hook to decide whether a CPU may be offlined. `smp.c` enforces the same policy in `loongson_cpu_disable`.

### Risks
Incorrect I/O master classification can either prevent useful hotplug or allow offlining a CPU needed for platform I/O/interrupt duties.

### Test Signals
Check `/sys/devices/system/cpu/cpu*/online` behavior and CPU hotplug attempts for I/O master and non-master CPUs. Validate consistency with `loongson_cpu_disable`.
