# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_strerror.c

Purpose: maps libfdt integer return codes to stable human-readable strings.

Important APIs/functions/types: `struct fdt_errtabent` stores a string pointer. `FDT_ERRTABENT()` initializes designated entries for every known `FDT_ERR_*` value through `FDT_ERR_ALIGNMENT`. `fdt_strerror()` returns special messages for positive offsets/lengths and zero, table strings for known negative errors, and `<unknown error>` otherwise.

Control flow/state: static immutable table indexed by positive error number after negating the passed error value.

Dependencies/integration: depends on error-code definitions in `libfdt.h`. Used by CLI tools and callers that surface libfdt failures.

Risks: table must stay synchronized with `FDT_ERR_MAX`; missing entries silently report unknown for new errors. Positive libfdt returns are not errors and are deliberately described as valid offsets/lengths.

Test signals: all known negative errors, zero, positive offsets, out-of-range negative codes, and any future error-code additions.
