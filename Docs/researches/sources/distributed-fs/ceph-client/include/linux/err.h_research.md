# sources/distributed-fs/ceph-client/include/linux/err.h

Purpose: standard kernel error-pointer encoding helpers.

Important APIs/types/functions: `MAX_ERRNO`, `IS_ERR_VALUE()`, `ERR_PTR()`, `INIT_ERR_PTR()`, `ERR_PTR_PCPU()`, `IOMEM_ERR_PTR()`, `PTR_ERR()`, `PTR_ERR_PCPU()`, `IS_ERR()`, `IS_ERR_PCPU()`, `IS_ERR_OR_NULL()`, `ERR_CAST()`, `PTR_ERR_OR_ZERO()`.

Control flow: APIs that normally return pointers encode negative errno values in the high invalid pointer range; callers test with `IS_ERR*()` and recover errno with `PTR_ERR()`.

State/persistence: no state. Encoded values are transient return values.

Dependencies/integration: sparse address-space annotations (`__iomem`, `__percpu`), compiler `__must_check`, branch prediction, and broad kernel pointer-return conventions.

Risks/test signals: risks are dereferencing encoded errors, mixing NULL and ERR_PTR semantics, losing address-space qualifiers, and returning positive values through `ERR_PTR`. Test call sites with allocation/probe failures, sparse warnings, and static analysis for missing `IS_ERR` checks.
