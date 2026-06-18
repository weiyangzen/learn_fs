# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cpc.h

Purpose: Cluster Power Controller register interface for MIPS CPS platforms. It is included through `mips-cps.h`.

Important APIs/types/functions: Exposes `mips_cpc_base`, `mips_cpc_default_phys_base()`, `mips_cpc_probe()`, and `mips_cpc_present()`. Accessor macros generate global, core-local, and core-other register accessors. Registers include CPC access, sequencer delays, rail/reset timing, revision, CM power-up control, mirrored config, endianness system config, core command, state/config, other-core select, VP stop/start/running, and per-core config. Lock helpers `mips_cpc_lock_other()` and `mips_cpc_unlock_other()` guard redirected core access when `CONFIG_MIPS_CPC` is enabled.

Control flow, state, and persistence: Probe maps CPC registers; callers issue core power commands and VP run/stop commands through generated accessors. Persistent state is in CPC hardware and exported base pointer.

Dependencies and integration: Depends on CPS accessors and CM locking. It integrates with SMP hotplug, power management, cluster bring-up, and multi-cluster topology code.

Risks and test signals: Power-state command sequencing can hang cores if issued to the wrong redirected core or without locks. Test core power-up/power-down/reset, VP stop/run, endian configuration, and CPC absence paths.
