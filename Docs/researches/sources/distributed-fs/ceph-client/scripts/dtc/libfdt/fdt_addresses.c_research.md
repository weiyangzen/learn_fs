# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_addresses.c

Purpose: helpers for reading address/size cell counts and appending encoded address ranges to properties.

Important APIs/functions: private `fdt_cells()` reads a named cell-count property, validates exact `fdt32_t` length, converts endian, and enforces `FDT_MAX_NCELLS`. `fdt_address_cells()` returns `#address-cells`, rejects zero, and defaults missing values to 2. `fdt_size_cells()` returns `#size-cells` and defaults missing values to 1. `fdt_appendprop_addrrange()` encodes an address and size as one- or two-cell values according to the parent and appends via `fdt_appendprop()`.

Control flow/state: stateless. The range helper builds a stack buffer of up to two 64-bit values and appends the encoded prefix length determined by cell counts.

Dependencies/integration: relies on read-only `fdt_getprop`, write-side `fdt_appendprop`, endian store helpers `fdt32_st`/`fdt64_st`, and error codes from `libfdt.h`.

Risks: intentionally only supports address and size cell counts of 1 or 2 in `fdt_appendprop_addrrange()`, despite `FDT_MAX_NCELLS` allowing up to 4. It validates 32-bit address overflow including range end overflow for one-cell addresses.

Test signals: missing/default cell counts, malformed property lengths, zero address cells, counts above max, one-cell overflow cases, two-cell encoding, and append failure propagation.
