# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/time.c

Purpose: PA Semi boot-time provider.

Important APIs and control flow: `pas_get_boot_time` returns a fixed `mktime64(2006, 1, 1, 12, 0, 0)` value and is installed by the PA Semi machine descriptor.

State, dependencies, and risks: there is no runtime state. Dependencies are generic time helpers and `ppc_md.get_boot_time`. Risks are obvious wall-clock inaccuracy until a real RTC/NTP source updates time; this may affect logs and filesystems early in boot. Test signals are machine boot without a real RTC path and subsequent correction by RTC platform devices or userspace time sync.
