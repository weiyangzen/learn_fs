# sources/distributed-fs/ceph-client/lib/fdt_strerror.c

## Purpose
Kernel wrapper for shared libfdt error-string conversion. It includes `linux/libfdt_env.h` and compiles `../scripts/dtc/libfdt/fdt_strerror.c`.

## Important APIs, Types, and Functions
The included API is `const char *fdt_strerror(int errval)`. It uses a static `fdt_errtable[]` mapping `FDT_ERR_*` numeric values to their symbolic names and returns special strings for positive offsets/lengths and zero.

## Control Flow
Positive inputs are reported as valid offsets/lengths, zero as no error, known negative libfdt errors as their `FDT_ERR_*` names, and unknown values as unknown errors.

## State and Persistence
Only a static error table exists. There is no mutable state or allocation.

## Dependencies and Integration Points
Depends on libfdt error definitions and kernel libfdt environment. It integrates with diagnostics in kernel code that reports libfdt return values.

## Risks
The table must be updated when new `FDT_ERR_*` values are introduced. Positive libfdt returns are not errors, so callers must not treat the returned positive-input string as failure evidence.

## Test Signals
Check zero, positive offsets, each known negative `FDT_ERR_*`, gaps in the table, and unknown negative values. Build tests should catch newly added error constants that lack expected diagnostics.
