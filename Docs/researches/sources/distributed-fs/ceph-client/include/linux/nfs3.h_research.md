# sources/distributed-fs/ceph-client/include/linux/nfs3.h

Purpose: Adds kernel-side NFSv3 constants over the UAPI NFSv3 definitions.

Important APIs, types, and functions: Exports `NFS3_POST_OP_ATTR_WORDS` and includes `uapi/linux/nfs3.h`. Detected source surface: 14 lines; includes `uapi/linux/nfs3.h`; macros `NFS3_POST_OP_ATTR_WORDS`, `_LINUX_NFS3_H`; structs none; enums none; typedefs none; function-like declarations/helpers none.

Control flow: There is no runtime flow; XDR code uses the constant for sizing post-op attribute buffers.

State and persistence behavior: No runtime state is stored.

Dependencies and integration points: Depends on UAPI NFSv3 procedure/status/type definitions and NFS XDR code.

Risks and test signals: Risk is XDR buffer sizing drift if protocol attr encoding changes. Test NFSv3 getattr/write/rename replies and XDR decode bounds.
