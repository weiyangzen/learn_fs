# sources/distributed-fs/ceph-client/lib/bootconfig.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bootconfig.c` implements the Linux extra boot config parser and query API. It copies bootconfig text into init memory, tokenizes the ASCII key/value syntax in place, builds a compact `struct xbc_node` tree, and exposes lookup/iteration helpers for early boot consumers. The source was read as a complete 1009-line file for this report.

## Important APIs, Types, and Functions

Key public entry points are `xbc_init`, `_xbc_exit`, `xbc_get_info`, `xbc_root_node`, `xbc_node_index`, `xbc_node_get_parent`, `xbc_node_get_child`, `xbc_node_get_next`, `xbc_node_get_data`, `xbc_node_find_subkey`, `xbc_node_find_value`, `xbc_node_compose_key_after`, `xbc_node_find_next_leaf`, and `xbc_node_find_next_key_value`. When `CONFIG_BOOT_CONFIG_EMBED` is enabled, `xbc_get_embedded_bootconfig` exposes linker-provided embedded bootconfig data. Internal parser state is global `__initdata`: `xbc_nodes`, `xbc_node_num`, `xbc_data`, `xbc_data_size`, `last_parent`, `xbc_err_msg`, `xbc_err_pos`, `open_brace`, and `brace_index`.

## Control Flow

`xbc_init()` rejects duplicate initialization and invalid sizes, allocates `xbc_data` and the node array, copies and terminates the input, then calls `xbc_parse_tree()` followed by `xbc_verify_tree()`. `xbc_parse_tree()` repeatedly finds delimiters with `strpbrk()` and dispatches to key, key/value, open-brace, close-brace, comment, semicolon, and newline handlers. Key parsing splits dot-separated names through `__xbc_parse_keys()` and inserts or reuses nodes with `__xbc_add_key()`. Value parsing supports quoted strings, comments, `=`, `:=` overrides, `+=` array append, comma arrays, and brace-close after values. Lookup helpers descend by dotted path, leaf iteration walks depth-first, and key composition walks parents back to the requested root.

## State and Persistence Behavior

All parser output is kept in init-time global memory. The parser mutates its copy of the input by replacing delimiters with NUL terminators and storing node data as 16-bit offsets with an `XBC_VALUE` flag. `_xbc_exit()` frees both buffers through either memblock or libc shims, clears counts, and resets brace tracking. There is no file persistence; lifetime is the boot/init lifecycle unless the tools build uses the user-space allocation path.

## Dependencies and Integration Points

The file depends on `linux/bootconfig.h` limits and node helpers, kernel allocation via memblock under `__KERNEL__`, string/ctype helpers, `WARN_ON`, and the tools/bootconfig user-space test shim. Boot code and `/proc/bootconfig` style consumers integrate through the exported `xbc_*` query functions after early boot passes the appended or embedded bootconfig blob.

## Risks and Edge Cases

The parser is highly stateful and mutates `last_parent`, so malformed brace nesting, empty keys, array appends, and duplicate value operations are the main correctness risks. Node and data offsets are bounded by `XBC_NODE_MAX`, `XBC_DATA_MAX`, `XBC_DEPTH_MAX`, and `XBC_KEYLEN_MAX`; overflow and deep trees must fail cleanly. Quoted values cannot escape quote characters. `+=` and `:=` must preserve subkeys and array ordering. Error offsets depend on the mutated buffer and need to remain meaningful for diagnostics.

## Test Signals

Useful tests are the tools/bootconfig parser sanity tests, malformed input cases for braces, comments, quotes, invalid keywords, depth/key length overflow, duplicate assignment, `:=` override, and `+=` arrays. Runtime signals include successful `xbc_get_info()`, deterministic dotted-key lookup, leaf iteration order, clean `_xbc_exit()`/reinit cycles, and embedded bootconfig size/path coverage when `CONFIG_BOOT_CONFIG_EMBED` is enabled.

## Read Coverage

Source read size: 1009 lines, 22786 bytes.
