# sources/distributed-fs/ceph-client/include/linux/bootconfig.h

Purpose: Declares the Extra Boot Config parser interface and compact tree representation used during early boot, plus a limited userspace-compatible surface for `tools/bootconfig` sanity tests. It defines how bootconfig data embedded in initrd or kernel image is identified, checksummed, parsed, traversed, and released.

Important APIs/types/functions: Constants define the `#BOOTCONFIG\n` magic, 4-byte alignment, maximum data size, node count, key length, and nesting depth. `xbc_calc_checksum()` performs the additive checksum used with size and magic when appending bootconfig to initrd. `struct xbc_node` is a packed 16-bit index node with `next`, `child`, `parent`, and tagged `data` fields; `XBC_VALUE` distinguishes value nodes from key nodes. Raw accessors include `xbc_root_node()`, node index/parent/child/next/data getters. Tree APIs include `xbc_node_find_subkey()`, `xbc_node_find_value()`, leaf/key-value iteration helpers, and `xbc_node_compose_key_after()`. Top-level lifecycle calls are `xbc_init()`, `xbc_get_info()`, `_xbc_exit()`, and `xbc_exit()`. `xbc_get_embedded_bootconfig()` is present only with `CONFIG_BOOT_CONFIG_EMBED`.

Control flow: Boot code detects appended or embedded bootconfig, validates checksum/magic/size externally, calls `xbc_init()` on the buffer, then consumers traverse key/value nodes with find helpers or iterator macros. Key-only entries return zero-length strings with NULL value-node pointers. Cleanup calls `_xbc_exit(false)` through `xbc_exit()`.

State/persistence: Parser state is early-init global/static state managed by `xbc_init()` and `_xbc_exit()`. Nodes store offsets/indices into parser-managed data; no long-term persistence is promised after cleanup. Most APIs are annotated `__init`.

Dependencies/integration: Kernel mode includes `linux/kernel.h` and `linux/types.h`; non-kernel inclusion is reserved for bootconfig tooling. Integrates with initrd assembly, early command-line handling, and embedded bootconfig options.

Risks/test signals: Risks include malformed nesting, array/value confusion, off-by-one in packed 15-bit data offsets, key composition truncation, and userspace tool drift. Test signals include `tools/bootconfig` parser tests, booting with appended and embedded configs, malformed checksum/magic cases, array iteration, max depth/key length/data size boundaries, and early-boot memory sanitizer coverage where available.
