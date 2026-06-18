<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf.h

Purpose: Defines s390 CPU Measurement Facility counter and sampling structures plus instruction wrappers.

Important APIs/types/functions: Interrupt masks, `cpumf_ctr_info`, sampling info/request/entry/trailer structures, `cpum_cf_avail()`, `cpum_sf_avail()`, `qctri()`, `lcctl()`, `ecctr()`, `stcctm()`, `qsi()`, and `lsctl()`. Source-visible declarations include: #define _ASM_S390_CPU_MF_H; #define CPU_MF_INT_SF_IAE (1 << 31) /* invalid entry address */; #define CPU_MF_INT_SF_ISE (1 << 30) /* incorrect SDBT entry */; #define CPU_MF_INT_SF_PRA (1 << 29) /* program request alert */; #define CPU_MF_INT_SF_SACA (1 << 23) /* sampler auth. change alert */; #define CPU_MF_INT_SF_LSDA (1 << 22) /* loss of sample data alert */; #define CPU_MF_INT_CF_MTDA (1 << 15) /* loss of MT ctr. data alert */; #define CPU_MF_INT_CF_CACA (1 << 7) /* counter auth. change alert */; #define CPU_MF_INT_CF_LCDA (1 << 6) /* loss of counter data alert */; #define CPU_MF_INT_CF_MASK (CPU_MF_INT_CF_MTDA|CPU_MF_INT_CF_CACA| \.

Control flow: Availability helpers test facilities, instruction wrappers execute CPU-MF operations and return condition-code status, and perf sampling code consumes packed hardware entry formats.

State and persistence behavior: Persistent state is CPU-MF control registers, counter sets, sampling buffers, and trailer metadata.

Dependencies and integration points: Direct includes are #include <linux/errno.h>, #include <linux/kmsan-checks.h>, #include <asm/asm-extable.h>, #include <asm/facility.h>, #include <asm/asm.h>. Integrated with Integrates perf events, hardware sampling, PMU interrupts, facility bits, and low-level condition-code handling..

Risks: Packed layouts and condition-code meanings are hardware ABI. Sampling loss/alert bits require careful interpretation to avoid misleading perf data.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 286 lines, 8717 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf.h -->
