# sources/distributed-fs/ceph-client/include/linux/kcov.h

## Purpose
Declares the Kernel Coverage runtime hooks used by compiler sanitizer coverage instrumentation and remote coverage collection.

## Important APIs, Types, And Functions
With `CONFIG_KCOV`, `enum kcov_mode` defines disabled/init/trace-PC/trace-CMP/remote states. APIs include `kcov_task_init()`, `kcov_task_exit()`, context-switch markers, `kcov_remote_start()`, `kcov_remote_stop()`, subsystem-specific remote helpers, `kcov_common_handle()`, and sanitizer coverage callbacks for PC, comparisons, constants, and switches.

## Control Flow
Tasks initialize KCOV state, userspace configures tracing through the UAPI, and compiler callbacks append PCs or comparison operands to per-task buffers. Remote coverage sections allow work not directly running in the userspace task to be associated with a handle. Context-switch markers suppress unsafe collection during scheduler transitions.

## State And Persistence
Coverage mode, buffers, and remote handles are per-task or remote-runtime state. Coverage is transient and consumed by fuzzers or tests.

## Dependencies And Integration Points
Depends on scheduler/task state, `uapi/linux/kcov.h`, interrupt context helpers, and compiler sanitizer coverage instrumentation. Integrates with syzkaller-style fuzzing and subsystem remote handles, especially USB and common handles.

## Risks
Remote coverage currently lacks nested task-context support; softirq wrappers guard a specific workaround. Incorrect start/stop pairing leaks coverage context. Disabled builds compile all helpers to no-ops.

## Test Signals
Signals include KCOV UAPI tests, compiler callback coverage, comparison tracing, remote handle collection, context-switch suppression, USB softirq paths, and disabled-build compilation.
