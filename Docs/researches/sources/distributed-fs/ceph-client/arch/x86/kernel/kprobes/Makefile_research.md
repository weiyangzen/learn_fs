# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/Makefile

Purpose: Selects the x86 kprobes implementation objects for the kernel build based on probe-related configuration symbols.

Important APIs/types/functions: no runtime API. Build rules add `core.o` for `CONFIG_KPROBES`, `opt.o` for `CONFIG_OPTPROBES`, and `ftrace.o` for `CONFIG_KPROBES_ON_FTRACE`.

Control flow: kbuild evaluates the three `obj-$(CONFIG_...)` lines and links only the objects needed by the configured feature set. `core.o` is the baseline architecture implementation; `opt.o` adds jump-optimized probes; `ftrace.o` adds dynamic ftrace-backed probes.

State and persistence: no runtime state. The persistent effect is compile-time inclusion or exclusion of architecture probe features.

Dependencies and integration points: integrates with top-level x86 kernel build rules and Linux kbuild config expansion. It mirrors the dependency layering in source: `opt.c` and `ftrace.c` both include `common.h` and rely on core kprobes data structures.

Risks: missing `core.o` when optional objects are enabled would break symbols such as `current_kprobe` and instruction-copy helpers. Accidental unconditional linking of optional objects would introduce unresolved references when their feature configs are off.

Test signals: build matrix should include `CONFIG_KPROBES=n`, baseline kprobes only, optprobes enabled, ftrace kprobes enabled, and both optional features enabled.
