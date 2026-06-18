# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/sleep.h

## Purpose
`sleep.h` is the small private header shared by x86 ACPI sleep C and assembly code. It declares the cross-language variables and entry points used to transfer control between `sleep.c`, `wakeup_32.S`, and `wakeup_64.S`.

## Important APIs, Types, and Functions
- Shared state declarations: `saved_video_mode`, `saved_magic`, and `wake_sleep_flags`.
- 32-bit resume symbol: `wakeup_pmode_return`.
- 64-bit wake entry: `wakeup_long64()`.
- Low-level suspend entry: `do_suspend_lowlevel()`.
- C low-level suspend function: `x86_acpi_suspend_lowlevel()`.
- Assembly-callable ACPI sleep bridge: `x86_acpi_enter_sleep_state(u8 state)`.

## Control Flow
`sleep.c` includes this header to call `do_suspend_lowlevel()` and to set or reference symbols defined in assembly. The assembly files include or match these declarations so they can call `x86_acpi_enter_sleep_state()` and publish resume symbols.

## State and Persistence Behavior
The declared variables are part of the suspend/resume handoff. `saved_magic` is used by wakeup assembly as an integrity/sanity marker; `saved_video_mode` is written into the real-mode wakeup header; `wake_sleep_flags` is shared with wakeup paths.

## Dependencies and Integration Points
The header depends only on kernel linkage declarations and ACPI status typing supplied by includers. Its integration point is the private ACPI sleep implementation under `arch/x86/kernel/acpi`.

## Risks
- Type or symbol mismatches between C and assembly can break low-level suspend or resume.
- Because these are low-level externs, missing configuration guards can expose symbols not defined in a given build mode.

## Test Signals
- Build both 32-bit and 64-bit ACPI sleep configurations.
- Use `nm`/link checks for `saved_magic`, `do_suspend_lowlevel`, `wakeup_long64`, and `wakeup_pmode_return` in the corresponding builds.
- Run S3 suspend/resume smoke tests.
