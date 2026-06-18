# sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-smi.c

Purpose: implements a legacy Intel SpeedStep CPUFreq driver that controls mobile Pentium III systems through an IST/SMI BIOS interface. It can obtain SMI port/command/signature from BIOS `ist_info` or module parameters.

Important APIs and functions: `speedstep_smi_ownership()` requests BIOS interface ownership via inline x86 `out` to the SMI port. `speedstep_smi_get_freqs()` asks BIOS for low/high MHz when the event field indicates a safe implementation, otherwise init falls back to `speedstep_get_freqs()`. `speedstep_set_state()` issues `SET_SPEEDSTEP_STATE` SMI commands with up to five retries and interrupt-enabled waits between failed attempts. CPUFreq hooks are `speedstep_cpu_init()`, `speedstep_target()`, `speedstep_get()`, and `speedstep_resume()`.

Control flow and state: global state stores `smi_port`, `smi_cmd`, `smi_sig`, detected processor enum, and a two-entry frequency table. Init filters x86 IDs, narrows supported processors to PIII variants, validates or fills SMI parameters, then registers the CPUFreq driver. Policy init is CPU0-only and reacquires SMI ownership on resume.

Dependencies and integration points: depends on `asm/ist.h`, inline 32-bit register conventions around SMI calls, module parameters, the shared SpeedStep library, CPUFreq table verification, and KVM-unrelated bare-metal BIOS behavior.

Risks and test signals: risks include firmware hangs on early systems, raw inline assembly assumptions, SMI calls under preemption/IRQ constraints, module parameter spoofing of signature, fallback probing that toggles real CPU states, and `speedstep_get()` returning `-ENODEV` through an unsigned return type for nonzero CPUs. Test signals include ownership result zero, sane BIOS-provided MHz values, fallback low/high probing success when BIOS call is disabled, retries resolving transient DMA-related failures, and resume reacquiring ownership.
