# sources/distributed-fs/ceph-client/scripts/generate_builtin_ranges.awk

## Purpose
`generate_builtin_ranges.awk` generates address range records that map built-in module code/data ranges inside vmlinux sections back to module names.

## Important APIs, Types, and Functions
`get_module_info()` maps object files to module names by reading adjacent `.cmd` files and validating against `modules.builtin`. `update_entry()` stores sorted range records. Main AWK patterns parse `modules.builtin`, `vmlinux.map`, and optionally `vmlinux.o.map`, supporting both GNU ld and LLVM lld map formats.

## Control Flow
Phase one records built-in module names. Phase two parses top-level linker map sections, bases, anchors, section addends, and detects whether a `vmlinux.o.map` pass is needed. Phase three records contiguous object ranges by module, clamping suspicious end offsets. The `END` block inserts anchor records and prints entries sorted by adjusted address.

## State and Persistence Behavior
State is held in AWK associative arrays: module validation, object-to-module cache, section bases/sizes/addends, anchors, range entries, and counts. Output is stdout only.

## Dependencies and Integration Points
It depends on GNU awk features such as `ARGIND`, `strtonum()`, and `asorti()`. It is part of the kernel build pipeline that produces `modules.builtin.ranges`.

## Risks and Test Signals
Linker map format drift is high risk. Address handling strips high hex digits to avoid AWK integer limits, which assumes kernel address ranges fit the remaining bits. `.cmd` parsing differs for C and Rust module variables. Test GNU ld and lld maps, direct-object and `vmlinux.a` links, multi-module objects, anchors, ignored sections, and modules with hyphen/underscore names.
