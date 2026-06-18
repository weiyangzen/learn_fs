# sources/distributed-fs/ceph-client/arch/x86/include/asm/microcode.h

## Purpose
Defines x86 microcode loader interfaces, CPU signature structures, Intel microcode blob layout, revision helpers, and late-loading NMI hooks.

## Important APIs, Types, And Functions
Types include `struct cpu_signature`, `struct ucode_cpu_info`, `struct microcode_header_intel`, and `struct microcode_intel`. Functions include `load_ucode_bsp()`, `load_ucode_ap()`, `microcode_bsp_resume()`, `microcode_loader_disabled()`, `intel_microcode_get_datasize()`, `intel_get_platform_id()`, `intel_get_microcode_revision()`, `microcode_nmi_handler()`, `microcode_offline_nmi_handler()`, and `microcode_nmi_handler_enabled()`. `initrd_start_early` exposes early initrd location.

## Control Flow
Early BSP/AP loaders apply microcode during boot or resume. Intel revision reads write zero to `MSR_IA32_UCODE_REV`, executes CPUID leaf 1, then reads the revision MSR. Late loading can enable an NMI handler through a static key.

## State And Persistence
State includes per-CPU signature/revision data, loaded microcode payload pointers, and CPU microcode hardware state. Updates persist until reset and are not filesystem-persistent through this header.

## Dependencies And Integration Points
Depends on MSR helpers and Intel CPU support. It integrates with early initrd scanning, CPU hotplug, suspend/resume, Intel IFS public header needs, and late microcode synchronization.

## Risks And Edge Cases
Microcode updates are CPU- and platform-sensitive. Header struct layout must match Intel blob format. Late loading needs NMI coordination and can interact with mitigations and errata state.

## Test Signals
Boot-time microcode revision logs, CPU hotplug after update, resume tests, late-loading tests, Intel and non-Intel build coverage, and disabled-loader command-line coverage are useful.
