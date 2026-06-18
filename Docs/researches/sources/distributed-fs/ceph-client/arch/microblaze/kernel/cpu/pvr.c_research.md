# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/pvr.c

Purpose: provides raw access to MicroBlaze Processor Version Registers and probes whether usable PVR support exists.

Important APIs and state: `cpu_has_pvr()` inspects the PVR MSR bit and PVR0 flags, returning the selector used by `setup_cpuinfo()`. `get_pvr(struct pvr_s *p)` reads PVR0 through PVR11 with inline `mfs rpvrN` instructions.

Control flow: `cpu_has_pvr()` first reads saved MSR flags. If no PVR bit is set, it returns no support. Otherwise it reads PVR0 and distinguishes full versus partial support using `PVR0_PVR_FULL_MASK`.

State and persistence: no persistent state; callers store the resulting PVR data. The code only reads special registers.

Dependencies and integration: depends on assembler support for `rpvr` names and `asm/pvr.h` bit definitions. Used by CPU setup and kgdb.

Risks and test signals: return values and comments are easy to misread; setup code interprets `1` as full PVR and `2` as unsupported/partial fallback. Test on old cores without PVR, partial-PVR cores, and full-PVR cores, verifying boot path and `/proc/cpuinfo`.
