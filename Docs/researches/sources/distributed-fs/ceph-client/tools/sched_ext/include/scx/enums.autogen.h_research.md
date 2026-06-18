# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.autogen.h

Purpose: generated user-space enum initialization support for sched_ext skeletons.

Important APIs/functions: this header defines the generated side of `SCX_ENUM_INIT()` used by `compat.h` during `SCX_OPS_OPEN()`. It maps kernel BTF enum names and entries into skeleton rodata variables matching the BPF-side weak `__SCX_*` variables.

Control flow: the generated macro/function sequence reads enum values from vmlinux BTF through compatibility helpers and writes them into the skeleton before load.

State and persistence: mutates skeleton rodata initial values only; no persistent external state.

Dependencies and integration: included by `enums.h`, which is included by `common.h`. It relies on `compat.h` enum-reading helpers and must stay in sync with `enums.autogen.bpf.h`.

Risks: stale generation or missing BTF enum entries can leave values zero or fallback values. Because many schedulers use `SCX_SLICE_DFL`, DSQ IDs, and ops flags, bad enum initialization can break scheduling semantics.

Test signals: build loaders, inspect rodata values after `SCX_OPS_OPEN()`, and load on kernels with both matching and shifted enum values.
