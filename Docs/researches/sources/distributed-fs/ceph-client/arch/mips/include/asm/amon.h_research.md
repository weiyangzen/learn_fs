<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/amon.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/amon.h

**Purpose:** Declares Arbitrary Monitor (AMON) CPU availability and startup hooks.

**Important APIs/types/functions:** `amon_cpu_avail(int cpu)` reports monitor CPU availability; `amon_cpu_start(int cpu, unsigned long pc, unsigned long sp, unsigned long gp, unsigned long a0)` starts a CPU at a supplied context.

**Control flow:** Header only; platform SMP code calls the monitor implementation.

**State, dependencies, integration:** Integrates boot monitor CPU control with MIPS SMP bring-up.

**Risks and test signals:** Register argument order must match monitor firmware. Test secondary CPU startup with known PC/SP/GP/A0 values and unavailable CPU reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/amon.h -->
