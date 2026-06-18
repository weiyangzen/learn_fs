# sources/distributed-fs/ceph-client/tools/arch/x86/lib/inat.c

## Purpose
Implements lookup functions over generated x86 instruction attribute tables.

## APIs, Types, and Functions
Exports `inat_get_opcode_attribute()`, `inat_get_last_prefix_id()`, `inat_get_escape_attribute()`, `inat_get_group_attribute()`, `inat_get_avx_attribute()`, and `inat_get_xop_attribute()`. It includes generated `inat-tables.c`.

## Control Flow, State, and Persistence
Primary opcode lookup indexes `inat_primary_table`. Escape and group lookup derive table IDs from the current attribute, select a default table, then optionally switch to a last-prefix variant table. Group lookup combines the selected group entry with common group attributes. AVX and XOP lookups validate map/prefix ranges before indexing generated tables.

## Dependencies and Integration
Depends on `insn.h`, generated `inat-tables.c`, and constants from `inat.h`. `insn.c` is the main runtime consumer.

## Risks and Test Signals
Risks include missing generated tables, null variant tables returning zero attributes, and bad map bounds for VEX/XOP decoding. Test signals are table-generation builds, decoder cases for escaped opcodes, grouped opcodes with prefix variants, VEX map limits, XOP map limits, and unsupported opcodes returning zero attributes.
