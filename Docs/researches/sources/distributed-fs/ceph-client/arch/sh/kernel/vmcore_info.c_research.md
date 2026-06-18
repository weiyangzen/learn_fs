# sources/distributed-fs/ceph-client/arch/sh/kernel/vmcore_info.c

Purpose: contributes SuperH architecture-specific metadata to crash dump vmcore notes.

Important APIs and functions: `arch_crash_save_vmcoreinfo` emits `VMALLOC_START` through the `VMCOREINFO_SYMBOL` macro.

Control flow: called by generic crash/vmcoreinfo code during crash dump metadata generation and appends the architecture virtual mapping boundary needed by dump analyzers.

State and persistence: does not mutate runtime state beyond the vmcoreinfo note buffer; the emitted symbol persists only in the crash dump metadata.

Dependencies and integration: depends on `linux/vmcore_info.h`, `linux/mm.h`, and generic kdump/crash dump consumers.

Risks: incomplete architecture metadata can make postmortem virtual-to-physical analysis harder. This file currently exports only one symbol, so any future SH vmcore requirements must be added here.

Test signals: inspect `/sys/kernel/vmcoreinfo` or generated vmcore notes for `VMALLOC_START`; no direct source-local test exists.
