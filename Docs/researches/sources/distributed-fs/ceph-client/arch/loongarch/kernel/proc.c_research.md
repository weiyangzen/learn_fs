## sources/distributed-fs/ceph-client/arch/loongarch/kernel/proc.c

### Purpose
`proc.c` backs `/proc/cpuinfo` for LoongArch. It formats system type, per-CPU topology, CPU/FPU revision, frequency, BogoMIPS, TLB size, address widths, ISA level, feature flags, and hardware watchpoint counts through a `seq_file` iterator.

### Important APIs, Types, And Functions
The exported object is `cpuinfo_op`. Internal functions are `show_cpuinfo`, `c_start`, `c_next`, and `c_stop`. Data sources include `cpu_data`, `__cpu_family`, `__cpu_full_name`, `cpu_clock_freq`, `const_clock_freq`, `lpj_fine`, `cpu_pabits`, `cpu_vabits`, `get_system_type`, and CPU feature macros.

### Control Flow
The seq iterator maps positions to CPU numbers. `show_cpuinfo` skips offline CPUs under SMP, prints the system type once for CPU 0, computes display MHz and BogoMIPS with `do_div`, and emits feature strings conditionally based on global CPU capability flags.

### State, Persistence, And Dependencies
The file has no mutable state. It depends on CPU probing, time initialization, and SMP topology having populated `cpu_data` and frequency globals before users read `/proc/cpuinfo`.

### Integration Points
Generic procfs CPU info code uses `cpuinfo_op`. The reported feature names are user-visible ABI for tools parsing `/proc/cpuinfo`.

### Risks
Feature strings and field labels are de facto ABI; renaming can break scripts. The frequency/BogoMIPS math depends on valid `const_clock_freq` and `HZ`. Skipping offline CPUs means seq positions may not produce output for every possible CPU.

### Test Signals
Compare `/proc/cpuinfo` on single-core, SMP, hotplug, LSX/LASX/LBT, and watchpoint-capable systems. Verify CPU MHz against clocksource data and feature flags against CPUCFG probing.
