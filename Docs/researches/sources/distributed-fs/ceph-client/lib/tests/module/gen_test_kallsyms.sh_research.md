## sources/distributed-fs/ceph-client/lib/tests/module/gen_test_kallsyms.sh

### Purpose
This Bash generator creates C source files for synthetic kallsyms test modules. Depending on the target suffix, it emits modules with many exported symbols, a module that references one exported symbol from module A, or larger scaled symbol sets used to stress kallsyms lookup and compression behavior.

### Important APIs, types, and functions
Inputs are positional: `$1` target filename, `$2` number of symbols, and `$3` scale factor. The script derives `TEST_TYPE` from `lib/tests/module/test_kallsyms_*.c`. `gen_template_module_header()` writes SPDX, includes, and `pr_fmt`. `gen_num_syms(prefix, num)` emits global integer symbols named `auto_test_${prefix}_${i}` with zero-padded indexes and `EXPORT_SYMBOL_GPL()` for each. Data templates A/C/D emit exported symbol sets and a zero-returning `auto_runtime_test()`. Template B emits an `extern int auto_test_a_<middle>` declaration and returns that symbol from init-time runtime test. `gen_template_module_exit()` emits module init/exit and metadata.

### Control flow
The script computes `FIRST_B_LOOKUP` as 1 unless `NUM_SYMS > 2`, in which case it uses the midpoint. A `case` on `TEST_TYPE` writes the header, type-specific data, and common footer into `$TARGET`. Type C emits `NUM_SYMS * SCALE_FACTOR` symbols; type D emits twice that scaled number.

### State and persistence
The generator writes the generated C source at a hard-coded `DIR=lib/tests/module` path joined with the basename of the target argument. It does not preserve any prior content. There is no runtime state after generation; generated modules carry the exported symbols and runtime init function.

### Dependencies and integration points
It depends on Bash, `basename`, `sed`, `seq`, shell arithmetic, and kbuild invoking it with numeric config values. The emitted C depends on kernel module, init, printk, and symbol export APIs. The companion Makefile calls this script through `if_changed`.

### Risks and edge cases
The output path ignores the directory of `$1` and always writes under `lib/tests/module`, which may be surprising in out-of-tree or separate object builds. There is no input validation for missing, zero, negative, or nonnumeric `NUM_SYMS`/`SCALE_FACTOR`. Unknown target suffixes fall through silently and produce no file content update. Very large scale factors can generate huge source files and object files.

### Test signals
Useful signals are generated symbol counts, successful cross-module reference from B to A’s midpoint symbol, and successful compilation/loading of generated modules. Type C/D scaling provides stress coverage beyond the baseline A symbol count.
