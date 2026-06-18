## sources/distributed-fs/openafs/src/kopenafs/kopenafs.h

Purpose: `kopenafs.h` declares the minimal standalone AFS client syscall API compatible with Heimdal/KTH libkafs expectations.

Important APIs: it exposes `k_hasafs`, `k_setpag`, `k_haspag`, `k_unlog`, and `k_pioctl`, and includes `afs/vioc.h` for `VIOC*` constants and `struct ViceIoctl`.

State and persistence: no state in the header; declared functions can change process PAG/token state or issue cache-manager pioctls.

Dependencies and integration points: consumers link against `libkopenafs` and call `k_hasafs` before other functions. The header explicitly states the calls only work with native AFS clients, not the NFS translator.

Risks: the API is intentionally thin and reports only integer syscall-style status, so callers must inspect `errno` for detail.

Test signals: used by `test-setpag.c` and `test-unlog.c`.
