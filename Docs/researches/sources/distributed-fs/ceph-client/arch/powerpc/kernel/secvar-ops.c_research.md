# sources/distributed-fs/ceph-client/arch/powerpc/kernel/secvar-ops.c

Purpose: minimal registration point for the platform secure-variable backend used by PowerPC secure boot.

Important APIs/types/functions: global `const struct secvar_operations *secvar_ops __ro_after_init` and `set_secvar_ops()`.

Control flow: a platform backend calls `set_secvar_ops()` once during initialization. The function warns and returns `-EBUSY` if a backend is already registered; otherwise it stores the operations pointer for later users such as `secvar-sysfs.c`.

State and persistence: stores a single read-only-after-init function table pointer. No secure variables are stored here; persistence belongs to backend firmware such as PLPKS.

Dependencies and integration points: depends on `asm/secvar.h` for operation definitions and is used by pSeries PLPKS secure-variable code before sysfs exposure.

Risks: no validation is performed beyond single-registration; a backend with missing methods can crash later sysfs code. Registration order matters because `secvar-sysfs` late init requires `secvar_ops` to be set.

Test signals: build with secure variable backends, confirm first registration succeeds and duplicate registration returns `-EBUSY`, then verify sysfs initialization sees non-NULL operations.
