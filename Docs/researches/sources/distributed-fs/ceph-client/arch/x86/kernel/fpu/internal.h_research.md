# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/internal.h

## Purpose
Provides small internal helpers and declarations shared across x86 FPU implementation files.

## Important APIs, Types, And Functions
Declares `init_fpstate`, `fpstate_init_user()`, and `fpstate_reset()`. `use_xsave()` and `use_fxsr()` wrap CPU feature checks. `WARN_ON_FPU()` expands to runtime warnings only under `CONFIG_X86_DEBUG_FPU`.

## Control Flow
There is no runtime control flow beyond inline feature tests and debug assertions.

## State, Persistence, And Dependencies
No state is defined here except external declarations. It depends on CPU feature flags and debug configuration.

## Integration Points
Included by `init.c`, `core.c`, `regset.c`, and `signal.c` to keep feature checks and debug assertions consistent.

## Risks
Changing wrappers changes feature selection throughout the FPU subsystem. Making `WARN_ON_FPU()` active or inactive affects bug visibility versus overhead.

## Test Signals
Builds should resolve declared symbols, and debug FPU builds should warn on invalid state transitions while non-debug builds compile checks away safely.
