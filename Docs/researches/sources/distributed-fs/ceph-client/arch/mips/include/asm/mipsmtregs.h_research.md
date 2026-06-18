# sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsmtregs.h

Purpose: CP0 register definitions and inline instruction wrappers for MIPS Multi-Threading (VPE/TC) control.

Important APIs/types/functions: Provides read/write macros for MVPControl/MVPConf, VPEControl/VPEConf, TCStatus/TCBind/TCHalt/TCContext, plus assembly register names. Bitfields define MVP enable, VPE targeting, TC states, VPE/TC configuration, halt flags, and thread exception codes. Runtime helpers include `core_nvpes()`, `dvpe()`, `evpe()`, `dmt()`, `emt()`, `ehb()`, `mftc0()`, `mftgpr()`, `mftr()`, `mttgpr()`, `mttc0()`, `mttr()`, `settc()`, and numerous targeted VPE/TC CP0/GPR access macros. It also builds set/clear/change helpers for `mvpcontrol`.

Control flow, state, and persistence: Helpers emit MIPS MT instructions, use execution hazard barriers, and require callers to set a target TC before targeted access. State persists in CP0 MT registers and selected target TC/VPE context.

Dependencies and integration: Builds on `mipsregs.h`, CPU feature `cpu_has_mipsmt`, ISA-level macros, and toolchain fallback instruction encodings. Used by SMP/MT bring-up, hotplug, and low-level scheduler code.

Risks and test signals: Targeted TC operations are ordering-sensitive; missing `ehb` or wrong target can corrupt another thread context. Test VPE enable/disable, TC halt/restart, secondary thread startup, non-MT fallback, and microMIPS/toolchain fallback builds.
