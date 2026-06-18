<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-kargs.c -->
# sources/cloud-native/ostree/tests/test-kargs.c

## Purpose
`test-kargs.c` unit-tests `OstreeKernelArgs`, including append, delete, replace, duplicate handling, empty values, key-only arguments, and quoted values with spaces.

## Important APIs, Types, And Functions
Tests call `ostree_kernel_args_new`, `append`, `delete`, `new_replace`, `to_strv`, cleanup support, and private inspection helpers `_ostree_kernel_arg_get_kargs_table`, `_ostree_kernel_arg_get_key_array`, `_ostree_kernel_args_entry_get_key`, and `_get_value`. Utility predicates compare keys and values inside GLib arrays/hash tables.

## Control Flow
`test_kargs_append` populates a kernel-args object and checks internal tables and emitted string vectors. `test_kargs_delete` checks missing-key failures, deletion by key, deletion by key/value, duplicates, no-value entries, and multi-token quoted inputs. `test_kargs_replace` checks invalid replacements, ambiguous multi-value replacement failure, and successful key/value replacement.

## State And Persistence
All state is in-memory inside `OstreeKernelArgs`, with GLib containers representing ordered args and key-to-values mappings. No persistent files are used.

## Dependencies And Integration Points
The file tests private kernel argument parsing used by deployment and bootloader code that mutates kernel command lines.

## Risks And Test Signals
Kernel arg parsing is whitespace- and quote-sensitive. Passing signals include correct differentiation between missing value and empty string, consistent table/vector updates after deletion, duplicate removal one entry at a time, and error propagation through `G_IO_ERROR_FAILED`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-kargs.c -->
