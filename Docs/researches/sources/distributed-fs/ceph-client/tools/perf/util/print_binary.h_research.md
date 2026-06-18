# sources/distributed-fs/ceph-client/tools/perf/util/print_binary.h

## Purpose
This header declares the binary printing operation protocol and public helpers for dumping byte arrays.

## Important APIs, Types, and Functions
It defines `enum binary_printer_ops`, `binary__fprintf_t`, `binary__fprintf`, inline `print_binary`, and `is_printable_array`.

## Control Flow
The inline `print_binary` simply calls `binary__fprintf` with `stdout`. Full control flow is implemented in `print_binary.c`.

## State and Persistence
No state is declared. Callers provide optional callback-private `extra` data.

## Dependencies and Integration Points
It depends on standard `stddef.h` and `stdio.h`. The enum is a stable callback protocol between generic binary traversal and concrete output renderers.

## Risks
Callbacks must handle all enum operations and unsigned values used as sentinels. API callers must provide a nonzero `bytes_per_line`.

## Test Signals
Compile tests should verify callback signatures. Behavior tests should validate that custom printers receive operations in the documented line/data order.
