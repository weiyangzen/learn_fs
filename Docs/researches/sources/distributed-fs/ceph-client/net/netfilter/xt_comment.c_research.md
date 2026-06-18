# sources/distributed-fs/ceph-client/net/netfilter/xt_comment.c

Purpose: no-op `comment` match lets rules carry comments without changing packet decisions.

Important APIs/types/functions: `comment_mt()` and `comment_mt_reg` with `xt_comment_info`.

Control flow: module registers one family-independent match; every packet returns true; exit unregisters it.

State and persistence: comment bytes persist only as rule data; no runtime state. Dependencies include x_tables ABI and userspace save/restore tooling. Risks: minimal, mainly match-size ABI stability and ensuring comments do not affect logic. Test signals: always true, family-independent use, comment serialization, and unregister on unload.
