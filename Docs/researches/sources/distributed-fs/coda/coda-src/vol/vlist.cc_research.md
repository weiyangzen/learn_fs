# sources/distributed-fs/coda/coda-src/vol/vlist.cc

Purpose: implements the working C++ vnode-list entry helpers used to track per-fid operation state.

Important APIs: `VLECmp` compares two `vle` entries by fid after asserting same volume. `FindVLE` linearly searches a `dlist` for a matching `ViceFid`. `AddVLE` returns an existing entry or inserts a new `vle`.

Control flow/state: callers maintain a `dlist` of `vle` entries for an operation. `AddVLE` centralizes uniqueness by fid and initializes entry side state through the `vle` constructor.

Dependencies/integration: depends on Coda `dlist`, fid comparison macros, server types, and `vlist.h`. Risks include linear lookup cost, comparison assertions if misused across volumes, and caller responsibility for deletion after vnode pointers are released. Test signals: add duplicate fids, find missing/present fids, sort/compare same-volume entries, and clean destruction with `vptr == 0`.
