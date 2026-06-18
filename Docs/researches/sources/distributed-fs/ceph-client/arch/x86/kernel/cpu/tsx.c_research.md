# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/tsx.c

## Purpose
Controls Intel TSX enumeration and runtime enablement/disablement based on config defaults, `tsx=` command line, microcode capabilities, and transient-execution mitigation state.

## Important APIs, Types, And Functions
`enum tsx_ctrl_states` tracks auto/on/off/always-abort/unsupported. `tsx_parse_cmdline()` handles `tsx=on|off|auto`. `tsx_init()` performs boot CPU policy. `tsx_ap_init()` applies the selected policy on APs. Helpers write `MSR_IA32_TSX_CTRL`, `MSR_TSX_FORCE_ABORT`, and `MSR_IA32_MCU_OPT_CTRL`.

## Control Flow
Boot first disables TSX development mode where TAA-sensitive microcode exposes `RTM_ALLOW`. If `RTM_ALWAYS_ABORT` is visible, TSX CPUID is cleared and RTM/HLE caps are cleared. Otherwise, the code requires `ARCH_CAP_TSX_CTRL_MSR`; unsupported hardware ignores policy. Auto disables TSX on TAA-affected systems and enables it otherwise. AP initialization repeats the selected MSR operation without changing global CPUID feature bits.

## State, Persistence, And Dependencies
`tsx_ctrl_state` is `__ro_after_init` after command-line parsing and init. CPU capability bits for RTM/HLE/MSR_TSX_CTRL and MSR values persist for the running kernel. It depends on architecture capabilities, vulnerability detection, and Intel microcode behavior.

## Integration Points
Feeds mitigation policy and userspace CPUID enumeration. AP paths integrate with CPU bring-up. The feature bits influence libraries and applications deciding whether to use RTM/HLE.

## Risks
Late microcode can change `RTM_ALWAYS_ABORT`; the code avoids late CPUID feature churn but still must clear hardware enumeration on APs. Enabling TSX can weaken TAA mitigation expectations. Incorrect MSR capability detection risks #GP.

## Test Signals
Boot with `tsx=on`, `tsx=off`, and `tsx=auto` should produce expected RTM/HLE CPUID visibility. TAA-affected hardware should default off in auto mode. CPU hotplug should preserve the selected TSX policy.
