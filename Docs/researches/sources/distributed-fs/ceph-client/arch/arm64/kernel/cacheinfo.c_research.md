<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cacheinfo.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cacheinfo.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cacheinfo.c` detects arm64 cache hierarchy levels and populates generic cacheinfo leaves. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `MAX_CACHE_LEVEL`; types: `cache_type`, `cpu_cacheinfo`, `cacheinfo`; functions/prototypes/exports: `cache_line_size`, `get_cache_type`, `ci_leaf_init`, `detect_cache_level`, `early_cache_level`, `init_cache_level`, `populate_cache_leaves`. The file is 119 lines / 2725 bytes. Direct includes are `linux/acpi.h`, `linux/cacheinfo.h`, `linux/of.h`.

### Control Flow
The code reads cache type/level registers, determines instruction/data/unified leaves, and initializes per-CPU cacheinfo from firmware or architectural registers.

### State, Persistence, And Dependencies
Notable global/static state symbols are `cache_line_size`, `clidr`, `ctype`, `early_cache_level`, `init_cache_level`, `level`, `fw_level`, `populate_cache_leaves`. Detected cache metadata persists in per-CPU cacheinfo structures exposed to sysfs and scheduling/topology code. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong CLIDR interpretation or firmware override handling can expose incorrect cache topology and affect scheduling or diagnostics.

### Test Signals
Boot on varied cache hierarchies, inspect `/sys/devices/system/cpu/cpu*/cache`, and compare with ACPI/PPTT or device-tree data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cacheinfo.c -->
