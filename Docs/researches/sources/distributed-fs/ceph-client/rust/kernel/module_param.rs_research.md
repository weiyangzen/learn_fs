# sources/distributed-fs/ceph-client/rust/kernel/module_param.rs

Purpose: supports Rust module parameters by defining parse traits, storage access, and generated `kernel_param_ops` for integer parameter types.

Important APIs/types/functions: `KernelParam`, `ModuleParam`, unsafe extern `set_param<T>`, `impl_int_module_param!`, `ModuleParamAccess<T>`, `make_param_ops!`, and statics `PARAM_OPS_*` for integer types.

Control flow: C module-parameter code calls `set_param` with a string and `kernel_param`. The adapter validates `val`, converts it to `CStr`/`BStr`, parses `T`, casts the kernel param argument to `SetOnce<T>`, and populates it. `ModuleParamAccess::value` returns the populated value or the default. Generated ops expose only `set`; `get` and `free` are `None`.

State and persistence behavior: parameter state is in a `SetOnce<T>` plus default value created by the module macro. Parameters are currently write-once, read-only from Rust, and not readable through sysfs per comments.

Dependencies and integration points: depends on `bindings::kernel_param`, `kernel_param_ops`, `SetOnce`, string integer parsing, and the Rust `module!` macro that initializes parameter storage and C metadata.

Risks: `ModuleParam` is constrained to `Copy` because destructors during teardown could be unsound. A null `val` is rejected; future valueless arguments would need revised handling. Casting `param.arg` to `SetOnce<T>` relies on module macro layout. Re-population returns `EEXIST`, so repeated sysfs/module-load writes are not supported by this storage model.

Test signals: tests should parse every supported integer type, reject invalid strings and duplicate sets, verify default fallback, and verify generated `kernel_param_ops` call the right typed setter. Integration testing should cover built-in and loadable module parameter initialization.
