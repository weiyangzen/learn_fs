# sources/distributed-fs/ceph-client/net/appletalk/Makefile

Purpose: Kbuild manifest for the AppleTalk protocol module.

Important APIs, types, and functions: defines `obj-$(CONFIG_ATALK) += appletalk.o`, with `appletalk-y := aarp.o ddp.o`. Optional additions are `atalk_proc.o` under `CONFIG_PROC_FS` and `sysctl_net_atalk.o` under `CONFIG_SYSCTL`.

Control flow: enabling `CONFIG_ATALK` builds a composite object named `appletalk.o`. The base stack always includes AARP and DDP; procfs and sysctl interfaces are compiled only when their kernel infrastructure is enabled.

State and persistence: no runtime state in the Makefile. It persists build composition by tying object membership to `.config`.

Dependencies and integration points: aligns with `net/appletalk/Kconfig`, top-level `net/Makefile`, and conditional C preprocessor usage in `ddp.c` init/exit paths. The composite module exports symbols from DDP and AARP for AppleTalk drivers.

Risks: if `ddp.c` calls proc/sysctl init or exit helpers without matching Kbuild/preprocessor guards, configs without those options can fail. The build assumes `aarp.o` and `ddp.o` are inseparable because DDP initializes and cleans up AARP.

Test signals: build matrix with `ATALK=y/m`, `PROC_FS=y/n`, and `SYSCTL=y/n`; inspect `appletalk.o` membership; module load/unload should not reference absent optional helper symbols.
