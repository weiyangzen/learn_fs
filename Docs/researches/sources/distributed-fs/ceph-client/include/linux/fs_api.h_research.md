# sources/distributed-fs/ceph-client/include/linux/fs_api.h

Purpose: this compatibility header currently includes `<linux/fs.h>` and defines no additional API of its own. It likely exists as a source-level include shim for code that wants a stable `fs_api.h` name while consuming the normal Linux VFS declarations.

Important APIs and functions: all usable declarations come from `linux/fs.h`; this file contributes no types, macros, functions, state, or control flow.

State and persistence: none. Dependencies are entirely transitive through `linux/fs.h`.

Integration points, risks, and test signals: the risk is accidental expectation that this header provides a narrower or independent API contract. Include-order tests and build coverage are the only meaningful signals; deleting or expanding it should be checked against out-of-tree or generated code that includes `linux/fs_api.h`.
