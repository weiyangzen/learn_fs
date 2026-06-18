# sources/distributed-fs/ceph-client/drivers/of/pdt.c

## Purpose
Builds the initial Linux OF device-node tree from PROM firmware callbacks for Open Firmware style systems.

## Important APIs, types, and functions
Main entry is `of_pdt_build_devicetree()`. It uses `struct of_pdt_ops` callbacks and helpers `of_pdt_create_node()`, `of_pdt_build_tree()`, `of_pdt_build_prop_list()`, `of_pdt_build_one_prop()`, and `of_pdt_build_full_name()`.

## Control flow
The build stores PROM ops, creates `of_root`, recursively walks child and sibling phandles, creates nodes with phandle/name/properties/full name, and runs `of_alias_scan()` after the root tree exists.

## State and persistence behavior
Nodes and properties are allocated with `prom_early_alloc()` and become permanent early-boot OF state. SPARC assigns unique IDs; generic builds use firmware paths or fallback names.

## Dependencies and integration points
Depends on architecture PROM callbacks, early allocation, OF core structures, optional SPARC IRQ translation, and global `of_root`.

## Risks and edge cases
Firmware path failures produce `"name@unknownN"` names. Bad or empty property lengths become empty properties. Because memory is early/permanent, malformed firmware data has lasting effects.

## Test signals
Indirectly covered by OF lookup, alias, phandle, IRQ, and platform population behavior on architectures using PDT.
