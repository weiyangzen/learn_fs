# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt.h

Purpose: public raw FDT wire-format definitions: header, reserve entries, structure-block records, tag constants, magic, and versioned header sizes.

Important APIs/types/macros: `struct fdt_header` models all versioned header fields through version 17. `struct fdt_reserve_entry` stores 64-bit address/size pairs. `struct fdt_node_header` and `struct fdt_property` model variable-length structure-block entries. Constants include `FDT_MAGIC`, `FDT_TAGSIZE`, tags `FDT_BEGIN_NODE`, `FDT_END_NODE`, `FDT_PROP`, `FDT_NOP`, `FDT_END`, and header sizes `FDT_V1_SIZE` through `FDT_V17_SIZE`.

Control flow/state: no executable logic. The layout types are included by both C and, guarded by `__ASSEMBLER__`, assembly contexts.

Dependencies/integration: requires endian-qualified integer types from `libfdt_env.h` before inclusion through `libfdt.h`. Consumed by all libfdt C modules and DTC flatten/unflatten code.

Risks: these structs define on-disk/on-wire ABI. Field ordering, flexible arrays, and sizes must remain stable. Consumers must always convert `fdt32_t`/`fdt64_t` to CPU endian before arithmetic.

Test signals: compile-time layout expectations, header-size compatibility for all supported versions, tag parsing interoperability, and DTB round-trip tests across endian hosts.
