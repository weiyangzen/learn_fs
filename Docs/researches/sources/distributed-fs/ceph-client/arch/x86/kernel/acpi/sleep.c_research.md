# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/sleep.c

## Purpose
`sleep.c` provides x86-specific ACPI sleep and wakeup preparation, primarily for S3 suspend. It fills the real-mode wakeup header with protected-mode restoration data, sets the firmware wake vector address, bridges assembly low-level suspend code to `acpi_enter_sleep_state()`, and parses `acpi_sleep=` command-line options.

## Important APIs, Types, and Functions
- `acpi_get_wakeup_address()` returns the physical address of `real_mode_header->wakeup_start`.
- `x86_acpi_enter_sleep_state()` is an assembly-callable wrapper around `acpi_enter_sleep_state()`.
- `x86_acpi_suspend_lowlevel()` validates the wakeup header, stores video mode and protected-mode CPU state, sets magic values and wake targets, pauses graph tracing, and calls `do_suspend_lowlevel()`.
- `acpi_sleep_setup()` parses `s3_bios`, `s3_mode`, `s3_beep`, S4 hardware-signature options, NVS save options, old ordering, and blacklist bypass.
- `init_s4_sigcheck()` sets hypervisor guest hibernation signature checking defaults when configured.

## Control Flow
The generic ACPI sleep path calls the function pointer initialized in `boot.c` to `x86_acpi_suspend_lowlevel()`. The function validates the real-mode wakeup header signature, records video and real-mode flags, saves CR0/CR4 and selected MSRs into the wakeup header, sets protected-mode entry state differently for 32-bit and 64-bit builds, sets `saved_magic`, and then calls the architecture assembly `do_suspend_lowlevel()`. Assembly saves processor/register state, invokes `x86_acpi_enter_sleep_state(3)`, and resumes through architecture-specific wakeup code.

Command-line parsing occurs through `__setup("acpi_sleep=", ...)` and mutates global ACPI sleep policy before suspend. Hypervisor S4 signature behavior is initialized as an arch initcall before ACPI subsystem initialization.

## State and Persistence Behavior
The file writes persistent suspend-resume handoff state into the real-mode wakeup header, `saved_magic`, `initial_code`, `current->thread.sp` for 64-bit SMP resume, and `smpboot_control` for non-parallel startup. `acpi_realmode_flags` persists command-line S3 behavior. S4 hardware-signature and ACPI NVS policy changes persist for the boot.

## Dependencies and Integration Points
This code depends on real-mode trampoline data under `arch/x86/realmode`, low-level assembly in `wakeup_32.S` and `wakeup_64.S`, saved processor-state helpers, MSR access, ftrace graph tracing, SMP startup controls, ACPI core sleep entry, hibernation policy, and hypervisor detection.

## Risks
- Wakeup header corruption or signature mismatch aborts suspend.
- Saved MSR/CR state is CPU- and mode-specific; incorrect restoration can fail resume.
- 64-bit SMP temporarily abuses `current->thread.sp` so unwinders and startup code must tolerate the value while suspended.
- Low-level suspend has unusual call/return behavior, hence graph tracing is paused around it.

## Test Signals
- Run S3 suspend/resume on 32-bit and 64-bit x86 configurations.
- Validate `acpi_sleep=s3_bios,s3_mode,s3_beep,nonvs,old_ordering,nobl` parsing changes expected behavior.
- Test hibernation on hypervisor guests and bare metal for S4 hardware-signature policy.
- Confirm resume logs do not show wakeup header mismatch and CPU state restores cleanly.
