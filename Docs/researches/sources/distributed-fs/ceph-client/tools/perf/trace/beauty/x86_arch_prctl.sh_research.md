# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/x86_arch_prctl.sh

Purpose: Generates lookup tables for x86 `arch_prctl` codes split by numeric ranges.

Important APIs/types/functions: The `print_range` shell function emits an offset macro and a `static const char *x86_arch_prctl_codes_<n>[]` array for codes with prefixes `0x1`, `0x2`, and `0x4`.

Control flow: The script selects the x86 UAPI asm directory, then calls `print_range` three times with base offsets `0x1001`, `0x2001`, and `0x4001`. Each pass parses `ARCH_*` definitions and formats index expressions relative to the first entry.

State and persistence: stdout-only generator.

Dependencies and integration points: The generated arrays are consumed by x86 arch-prctl beauty code elsewhere in the perf tree.

Risks: Codes outside the three hard-coded ranges will be omitted. Regex only handles simple hex definitions.

Test signals: Regenerate and verify entries such as `ARCH_SET_GS`, `ARCH_SET_FS`, and newer arch-prctl codes from each range.
