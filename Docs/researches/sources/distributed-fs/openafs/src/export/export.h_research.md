# sources/distributed-fs/openafs/src/export/export.h

This header defines the userspace-to-kernel configuration contract and import descriptors for the AIX EXPORT extension. `struct k_conf` carries symbol count, symbol table size, string table size, and userspace addresses for both tables. `struct k_func` describes a function import destination and reserves a function descriptor. `struct k_var` describes a variable import surrogate and symbol name.

There is no runtime control flow. State is represented by these structures as passed through `SYS_CFGKMOD` or consumed by `import_kfunc`/`import_kvar`. Dependencies are AIX integer and address types such as `u_int`, `u_int64`, and `caddr_t`, plus `__XCOFF64__`/`AFS_64BIT_KERNEL` for descriptor width.

Integration is between `cfgexport.c`, `export.c`, and AIX OpenAFS kernel modules needing missing symbols. Risks are ABI mismatch between 32-bit and 64-bit builds, pointer-size assumptions, and caller responsibility for valid storage. Test signals are successful cfgexport-to-export configuration and import descriptors resolving real kernel symbols.
