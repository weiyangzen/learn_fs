# sources/distributed-fs/ceph-client/arch/x86/kernel/callthunks.c

## Purpose
This file implements x86 call thunk patching for call depth tracking mitigation. It rewrites compiler-recorded direct call sites so calls land on per-target padding containing the call-depth accounting template before reaching the original function.

## Important APIs, Types, and Functions
Important public entry points are `callthunks_patch_builtin_calls()`, `callthunks_translate_call_dest()`, module hook `callthunks_patch_module_calls()`, and BPF helper `x86_call_depth_emit_accounting()` when BPF JIT is enabled. Internals include `call_get_dest()`, `skip_addr()`, `patch_dest()`, `patch_call()`, `patch_call_sites()`, and `callthunks_setup()`. Debug builds export per-CPU call/return/stuff/context-switch counters and may create debugfs files.

## Control Flow
On boot, `callthunks_patch_builtin_calls()` checks `X86_FEATURE_CALL_DEPTH`, locks `text_mutex`, walks `__call_sites`, decodes each direct call, skips special entry/kexec/ftrace/switch targets, verifies source and target text ownership, installs the accounting template into target padding, and rewrites the call displacement to the padding. Module and live translation paths repeat this under `text_mutex`. BPF JIT can either detect an existing thunk or emit accounting bytes inline.

## State and Persistence
`thunks_initialized` records whether builtin patching completed. Patched kernel/module text and function padding are persistent until reboot or module unload. Debug counters are per-CPU runtime state. The `debug-callthunks` boot parameter enables verbose logging.

## Dependencies and Integration Points
The code depends on alternatives/text patching, instruction decoding, kallsyms/module text ranges, ftrace, kexec relocation ranges, Xen hypercall entry symbols, nospec branch mitigation definitions, BPF JIT, debugfs, and `text_mutex` synchronization.

## Risks and Test Signals
Risks include decoding non-call bytes, patching insufficient or non-NOP padding, targeting text outside validated ranges, racing text modification, or missing special entry points that already manage call depth. Test signals include boot log `Setting up call depth tracking`, absence of invalid padding warnings, module load tests with call thunk patching, BPF JIT execution, debugfs counter movement, and mitigation selftests.
