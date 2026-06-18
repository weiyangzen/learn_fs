# sources/distributed-fs/ceph-client/scripts/dtc/fdtput.c

Purpose: command-line utility for editing a DTB in place on disk by setting a property value or creating nodes.

Important APIs/functions/types: `enum oper_type` distinguishes property writes from node creation. `struct display_info` carries operation, type, element size, verbosity, and auto-path creation. `encode_value()` converts CLI strings into a raw property payload using util-decoded type/size, defaulting to 32-bit cells. `store_key_value()` resolves a node path then calls `fdt_setprop`. `create_paths()` walks path components and creates missing subnodes. `create_node()` splits parent/name and calls `fdt_add_subnode`. `do_fdtput()` reads the blob, dispatches the operation, and writes it back.

Control flow/state: `main()` validates arguments and flags, then `do_fdtput()` mutates the loaded blob and persists it only if all requested changes succeed. Auto-path mode can create intermediate nodes before writing the property or create full paths directly for node creation.

Dependencies/integration: uses libfdt read/write mutators and DTC util helpers for blob I/O and type parsing. It assumes the input blob has sufficient writable slack; unlike `fdtoverlay`, it does not grow via `fdt_open_into`.

Risks: `encode_value()` uses `int *` stores into a char buffer for 32-bit values, so alignment assumptions follow local platform behavior. Only one-byte and four-byte integer paths are fully stored despite accepting size metadata; two-byte values are effectively truncated through the byte path. `create_node()` temporarily writes NUL into the node path string.

Test signals: property writes for string/int/hex types, empty values, `-p` auto path creation, `-c` node creation, insufficient DTB space, missing parent diagnostics, and malformed type strings.
