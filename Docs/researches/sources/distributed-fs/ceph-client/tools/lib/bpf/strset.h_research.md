## sources/distributed-fs/ceph-client/tools/lib/bpf/strset.h

Purpose: Declares the opaque libbpf string-set interface implemented by `strset.c`.

Important APIs/types: `struct strset` is opaque. `strset__new()` creates a set with maximum data size and optional initial data. `strset__free()` releases it. `strset__data()`/`strset__data_size()` expose packed storage. `strset__find_str()` and `strset__add_str()` return offsets or negative errors.

Control flow: Header-only flow is limited to lifecycle contract: allocate, add/find strings, consume packed data, free.

State/persistence: The set owns all data internally. Callers should not retain the `strset__data()` pointer across operations that may grow the buffer unless the implementation contract is checked.

Dependencies/integration: Includes `<stdbool.h>` and `<stddef.h>`; paired with libbpf hashmap internals in the C file.

Risks: API uses integer offsets and negative errno values; offset 0 and error handling need caller care. Opaque type hides mutation/growth behavior.

Test signals: Compile users against the header alone and test error handling for `ERR_PTR` returns from `strset__new()` plus negative returns from find/add.
