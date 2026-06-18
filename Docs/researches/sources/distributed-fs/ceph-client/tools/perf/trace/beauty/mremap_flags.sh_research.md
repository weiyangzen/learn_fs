# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mremap_flags.sh

Purpose: Generates `MREMAP_*` flag names for `mremap(2)` formatting.

Important APIs/types/functions: It parses `tools/include/uapi/linux/mman.h` or a supplied directory and emits `static const char *mremap_flags[]`, including fallback `#define MREMAP_*` guards.

Control flow: It matches hex or digit constants, converts each value into `ilog2(value) + 1`, and formats both the array entry and conditional macro definition.

State and persistence: Stateless stdout generator.

Dependencies and integration points: Included by `mmap.c` and consumed by `strarray__scnprintf_flags`.

Risks: Composite values would be incorrectly treated as single-bit flags; currently `MREMAP_*` flags are expected to be bit values.

Test signals: Verify generated entries for `MREMAP_MAYMOVE`, `MREMAP_FIXED`, and related flags; trace `mremap` and confirm `new_address` masking in the consumer.
