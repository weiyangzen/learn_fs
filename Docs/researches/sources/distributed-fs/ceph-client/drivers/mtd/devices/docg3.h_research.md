## sources/distributed-fs/ceph-client/drivers/mtd/devices/docg3.h

Purpose: private DiskOnChip G3 hardware definition header. It describes IO-space layout, page/OOB/wear geometry, ECC constants, register offsets, command/sequence values, protection bits, cascade and per-floor state structures, logging macros, and a trace event for register IO.

Important APIs, types, and functions: `struct docg3_cascade` stores floor MTDs, shared MMIO base, BCH context, and mutex. `struct docg3` stores device pointer, cascade pointer, floor id, interface/reliable mode, max block, BBT cache, and OOB staging state. Constants define 512-byte data pages, 16-byte OOB, two planes, BCH(14,4) parameters, block layout, and all ASIC registers.

Control flow: no normal runtime functions are implemented, but the `TRACE_EVENT(docg3_io)` declaration is compiled into tracepoints when `docg3.c` defines `CREATE_TRACE_POINTS`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE docg3` rely on the Makefile include path.

State and persistence: the header defines all driver-private state layouts and the persistent flash geometry/protection interpretation used by `docg3.c`.

Dependencies and integration points: includes MTD and Linux tracepoint infrastructure. Consumed directly by `docg3.c`; its trace section integrates with ftrace/perf tooling.

Risks: constants encode reverse-engineered hardware behavior; small mistakes affect all addressing, ECC, protection, and suspend operations. The misspelled `DOC_ECCCONF1_UNKOWN*` names are harmless but signal undocumented bits.

Test signals: successful tracepoint compilation, register reads/writes decoded by `docg3_io`, geometry matching actual media size/OOB layout, BCH constants producing correct correction behavior, and sysfs/debugfs views mapping the expected protection registers.
