# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/match.c

Purpose: provides reusable x86 CPU match-table helpers for code that needs model, feature, stepping, platform, or vendor CPU-type selection.

Important APIs and flow: `x86_match_cpu()` scans an `x86_cpu_id` table until the valid-entry flag ends, matching against `boot_cpu_data` vendor, family, model, stepping bitmask, Intel platform mask, feature bit, and vendor-specific CPU type. `x86_match_vendor_cpu_type()` treats `X86_CPU_TYPE_ANY` as wildcard, intentionally treats hybrid CPUs as matching all CPU types, and otherwise compares Intel or AMD topology-provided type fields. `x86_match_min_microcode_rev()` reuses `x86_match_cpu()` and compares `driver_data` with the boot CPU microcode revision.

State and persistence: read-only against `boot_cpu_data`; no persistence or allocation.

Dependencies and integration: exported to modules and GPL users, and used by Intel EPB, errata, driver matching, and CPU feature code. It depends on stable `asm/cpu_device_id.h` table macros.

Risks and test signals: boot-CPU-only matching assumes homogeneous relevant features. Hybrid CPU wildcard behavior is intentional but can surprise code trying to target only performance or efficiency cores. Signals include module auto-match behavior, microcode-gated feature tests, and table terminator validation.
