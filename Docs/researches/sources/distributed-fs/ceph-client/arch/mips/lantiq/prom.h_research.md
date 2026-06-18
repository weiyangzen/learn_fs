# sources/distributed-fs/ceph-client/arch/mips/lantiq/prom.h

Purpose: defines common Lantiq SoC information structures and declarations shared by generic and SoC-specific PROM code.

Important APIs/types/functions: `struct ltq_soc_info` carries `name`, revision fields, `partnum`, `type`, `sys_type`, and `compatible`; declarations for `ltq_soc_detect()` and `ltq_soc_init()`.

Control flow: SoC-specific detection fills this structure; generic `prom_init()` formats and exposes it.

State and persistence: the structure is caller-owned and typically stored in generic `prom.c` static state.

Dependencies and integration: included by XWAY/Falcon PROM and sysctrl code.

Risks: fixed-size revision/system strings require bounded formatting by callers.

Test signals: compile checks for all SoC providers and boot log system type correctness.
