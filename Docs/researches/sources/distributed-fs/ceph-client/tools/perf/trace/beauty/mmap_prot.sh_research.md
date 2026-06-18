# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap_prot.sh

Purpose: Generates the `PROT_*` protection flag table for mmap-like syscall formatting.

Important APIs/types/functions: It emits `static const char *mmap_prot[]` and fallback `#define PROT_*` guards, omitting `PROT_NONE` because zero is handled specially in `mmap.c`.

Control flow: The script chooses generic and architecture mman header directories, reads generic common flags when the arch header includes generic mman content, then reads arch-specific definitions when present. Each hex value is converted to an `ilog2(value) + 1` slot.

State and persistence: Stateless stdout generator.

Dependencies and integration points: The output is included by `mmap.c` and consumed by `strarray__scnprintf_flags`.

Risks: Decimal or expression values are not matched. Zero-valued or mask-valued protections are intentionally not suitable for this generated bit table.

Test signals: Compare generated table entries to `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`, and arch-specific protection bits; trace mmap with combined protections.
