## sources/distributed-fs/coda/coda-src/volutil/physio.cc

Purpose: `physio.cc` supplies physical directory I/O callbacks for the Coda directory/buffer package, adapted for salvager-style use with in-memory/RVM-backed directory pages.

Important APIs/types/functions: exported callbacks include `ReallyRead`, `ReallyWrite`, `FidZap`, `FidEq`, and `FidCpy`. It references `DirHandle`, `DirInode`, `shadowDirPage`, `DirHtb`, `VFid`, and `VolumeChanged`. `PAGESIZE` is fixed at 2048 bytes.

Control flow: `ReallyRead` checks the shadow directory hash table first for an uncommitted page matching the directory fid/block, then falls back to the committed `DirInode` page array. `ReallyWrite` creates a new `shadowDirPage`, removes any prior matching shadow page, inserts the new one, and marks `VolumeChanged`. The Fid helpers zero, compare, or copy `DirHandle` values.

State and persistence behavior: writes are staged in the global directory hash table rather than written immediately to recoverable storage; later directory commit logic flushes shadow pages. Reads can observe staged pages before committed pages. The code mutates global `VolumeChanged`.

Dependencies/integration points: integrates with the directory package, Coda vnode/volume structs, `dirvnode.h`, `DirHtb`, and `shadowDirPage`. It is low-level support for volume utilities and salvage/commit flows that manipulate directory pages.

Risks: `while (nsdp = ...)` and similar patterns rely on assignment in condition. No bounds check is performed on `block` before indexing `dinode->Pages`. `ReallyWrite` allocates with `new` and depends on hash-table replacement to avoid leaks. It uses `printf` diagnostics rather than structured logging. The `extern VolumeChanged;` declaration lacks an explicit type in this old C style.

Test signals: directory page read/write unit tests should cover committed-only pages, staged page override, replacement of an existing staged page, missing inode/page behavior, and invalid block indices. Integration tests should commit staged pages and verify directory contents survive salvage.
