
# sources/distributed-fs/ceph-client/lib/test_dynamic_debug.c

## Purpose

This module exercises dynamic debug class maps and class-parameter plumbing. Loading the module or reading/writing the `do_prints` module parameter triggers a predictable set of `pr_debug()` and `__pr_debug_cls()` calls.

## Important APIs, Types, And Functions

`DD_SYS_WRAP()` creates dynamic debug class parameters backed by `struct ddebug_class_param` and `param_ops_dyndbg_classes`. Four class maps are declared: disjoint numeric bits, disjoint symbolic names, numeric verbosity levels, and symbolic verbosity levels. `do_cats()` emits category-class messages, `do_levels()` emits level-class messages, and `do_prints()` runs both.

## Control Flow And State

The module stores class-enable state in per-map `bits_*` variables exposed through module parameters such as `p_disjoint_bits`, `T_disjoint_bits`, `p_level_names`, and `T_level_names`. Init logs debug messages and calls `do_prints()`. Parameter get/set callbacks call `do_prints()` again and either return a fixed status string or accept the write.

## Dependencies And Integration Points

The file integrates with the dynamic debug subsystem through `DECLARE_DYNDBG_CLASSMAP`, `__pr_debug_cls`, and the class parameter ops. Userspace drives it through module parameters under sysfs and dynamic debug control files.

## Risks And Test Signals

Class id bases must match the enum values and stay within the shared 0-30 class id space. Test signals are whether dynamic debug queries can enable exactly the expected category or verbosity messages and whether parameter reads/writes trigger the same print stream without module reload.
