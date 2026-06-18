# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_sw.c

Purpose: sequential-write API for constructing a new DTB from scratch in a caller-supplied buffer.

Important APIs/functions: probes enforce write states: initial reserve-map state, structure-emission state, and completed state. `fdt_create_with_flags()` initializes an unfinished blob using `FDT_SW_MAGIC` and stores creation flags in `last_comp_version`; `fdt_resize()` safely moves an unfinished blob; `fdt_add_reservemap_entry()` and `fdt_finish_reservemap()` write reserve entries. `fdt_begin_node`, `fdt_end_node`, `fdt_property_placeholder`, `fdt_property`, and string helpers build the structure and reverse-growing strings block. `fdt_finish()` writes `FDT_END`, relocates strings after structure, fixes property name offsets, and restores final magic/version fields.

Control flow/state: state is encoded in header fields. During construction the strings block grows backward from the end of the buffer while the structure block grows forward; `fdt_finish()` compacts them into normal order.

Dependencies/integration: uses `fdt_next_tag`, raw offset helpers, endian macros, and flags from `libfdt.h`. `fdt_empty_tree.c` is a simple consumer.

Risks: calls in the wrong state return `-FDT_ERR_BADSTATE`. Name dedup can be disabled for speed/size tradeoffs. Failed property allocation rolls back newly added strings only if needed and possible.

Test signals: state-machine misuse, buffer exhaustion with forward/backward growth collision, no-name-dedup flag behavior, resize overlap cases, property placeholder writes, finish-time nameoff correction, and final tree validation.
