# sources/distributed-fs/ceph-client/tools/perf/scripts/python/mem-phys-addr.py

Purpose: `mem-phys-addr.py` resolves perf samples with `phys_addr` into `/proc/iomem` ranges and prints a count/percentage table by memory-resource type.

Important APIs and state: `IomemEntry` is an immutable dataclass for begin/end/indent/label lines. Global containers hold ranges by indentation, parent-child edges, maximum indent, counted memory types, and the first event name. `parse_iomem`, `find_memory_type`, `print_memory_type`, `trace_begin`, `trace_end`, and `process_event` are the main functions.

Control flow: `trace_begin` parses `/proc/iomem`, discovering hierarchy by indentation and parent lookup. `process_event` ignores events without samples or without `phys_addr`, stores the first event name, finds the deepest matching range via `bisect_right` over sorted ranges, and increments the matching entry counter. `trace_end` rolls child counts into parents and recursively prints nonzero entries ordered by descending count.

State and persistence: state is process-local and accumulates for the full perf-script stream. The only external read is `/proc/iomem`; output is stdout.

Dependencies, integration, risks, and tests: it relies on Python dataclasses, `bisect` with a `key` argument, `/proc/iomem` readability, and perf sample dictionaries including physical addresses. Risks include requiring newer Python for `bisect(..., key=...)`, assertion failure if indentation hierarchy is unexpected, and division by zero when no counted samples exist. Test signals are samples from physical-address capable perf events producing a non-empty memory type table.
