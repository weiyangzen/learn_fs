<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-type.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-type.h

**Purpose:** Provides config-filtered helpers for retrieving current and boot CPU type.

**Important APIs/types/functions:** `__get_cpu_type()` validates a CPU type against enabled `CONFIG_SYS_HAS_CPU_*` families, while `current_cpu_type()` and `boot_cpu_type()` read `cpu_data`.

**Control flow:** Switch cases are compiled only for selected CPU families; default is `unreachable()`.

**State, dependencies, integration:** Depends on `current_cpu_data` and `cpu_data[0]`. Used by feature and platform code to choose CPU-specific behavior.

**Risks and test signals:** Probe returning a CPU type not enabled in config reaches unreachable behavior. Test defconfigs for every enabled CPU family and QEMU generic selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-type.h -->
