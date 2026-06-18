# sources/distributed-fs/ceph-client/drivers/bus/omap_l3_noc.h

## Purpose
This header is the data model and SoC decode database for the OMAP L3 NOC error handler. It defines register offsets, status constants, core structs, transaction strings, target tables, master tables, flagmux layouts, and matched `struct omap_l3` templates for OMAP4, OMAP5, DRA7, and AM4372.

## Important APIs, Types, and Functions
Key types are `struct l3_masters_data`, `struct l3_target_data`, `struct l3_flagmux_data`, and `struct omap_l3`. Constants such as `L3_TARG_STDERRLOG_*`, `L3_FLAGMUX_REGERR0`, `L3_FLAGMUX_MASK0`, `CUSTOM_ERROR`, and `CLEAR_STDERR_LOG` define the register contract consumed by `omap_l3_noc.c`. `l3_transaction_type[]` maps opcodes to printable transaction classes.

## Control Flow
There is no executable control flow beyond static initialization. Probe in the C file selects one of the static `omap*_l3_data` templates through OF match data, then interrupt handling uses the selected pointer graph to translate flagmux bit indexes into target offsets and names.

## State and Persistence
Most tables are static mutable objects, not `const`, because runtime code stores ignore masks in `struct l3_flagmux_data`. The matched `struct omap_l3` template itself is copied at probe time, but its nested `l3_flagmux` pointers still reference these static flagmux records, so mask state is shared per driver image.

## Dependencies and Integration Points
The header depends on kernel macros such as `ARRAY_SIZE`, `BIT`, and I/O types supplied by includers. It is tightly coupled to OMAP L3 register manuals and to the implementation in `omap_l3_noc.c`.

## Risks and Test Signals
The risk is correctness of static data: bad target offsets, duplicate or placeholder master IDs, mismatched `mst_addr_mask`, or unsupported targets can make diagnostics misleading or cause a source to be masked. Test signals are accurate decoded master/target names on each compatible SoC and no out-of-bounds target handling during L3 fault injection.
