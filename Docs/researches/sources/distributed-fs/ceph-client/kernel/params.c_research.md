<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/params.c -->
# sources/distributed-fs/ceph-client/kernel/params.c

Purpose: Provides kernel/module command-line parameter parsing, standard parameter type operations, array/string handling, unsafe/lockdown checks, and sysfs exposure under `/sys/module/*/parameters`.

Important APIs/types/functions: `parse_args()`, `parameqn()`, `parameq()`, standard `param_set_*`, `param_get_*`, and `param_ops_*` for numeric, bool, invbool, bint, charp, string, and arrays; `param_set_uint_minmax()`, `kernel_param_lock()`, `kernel_param_unlock()`, `module_param_sysfs_setup()`, `module_param_sysfs_remove()`, `lookup_or_create_module_kobject()`, `__modver_version_show()`, and `module_destroy_params()`.

Control flow: `parse_args()` tokenizes space/comma-like kernel args using `next_arg()`, stops at `--`, and delegates each token to `parse_one()`. `parse_one()` matches dash/underscore-equivalent names, checks parameter level range, validates no-arg handling, locks the relevant module or built-in parameter mutex, checks unsafe/lockdown policy, invokes the setter, and reports errors. Standard setters parse with kstrtox helpers. `charp` parameters track kmalloced values for later freeing but can point into early boot command-line storage before slab is available. Sysfs setup builds a `parameters` attribute group per module/built-in module and routes reads/writes through parameter ops under lock.

State and persistence: Parameter values live in the variables pointed to by `kernel_param.arg`. `kmalloced_params` tracks dynamically allocated string parameter storage. Sysfs kobjects and attribute groups persist for built-in modules and loaded modules until removal. `module_kset` and `module_ktype` implement the `/sys/module` object model.

Dependencies/integration: Integrates with module loading, boot command-line parsing, sysfs/kobjects/ksets, security lockdown, kernel tainting, slab allocation, module version sections, and `CONFIG_MODULES`/`CONFIG_SYSFS`.

Risks: Setters may run during early boot before normal allocation/locking assumptions fully hold. `param_array()` temporarily writes NULs into the argument string, so callers must pass mutable buffers. Runtime DAC changes cannot make read-only params writable, but parameter ops themselves must enforce semantic constraints. Unsafe parameters taint the kernel; hardware parameters can be blocked by lockdown. `charp` lifetime depends on correct tracking through `kmalloced_params`.

Test signals: command-line parse of known/unknown params, dash versus underscore matching, `--` passthrough, null value rejection, no-arg bools, min/max validation, charp replacement/free before and after slab availability, array parsing limits/minimums, sysfs parameter permissions and writes, lockdown rejection of hardware parameters, unsafe tainting, and module unload parameter cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/params.c -->
