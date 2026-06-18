# sources/distributed-fs/glusterfs/xlators/meta/src/type-file.c

Purpose: implements the virtual `type` file under each xlator, exposing the translator type string.

Important APIs/types/functions: `type_file_fill()` writes `xl->type` plus newline. `meta_type_file_hook()` attaches `type_file_ops` and copies parent xlator context.

Control flow: `xlator-dir.c` exposes `type`; lookup binds the parent xlator and readv renders the type through `strfd`.

State and persistence behavior: no persistent state; output reflects the target xlator's live `type` field at first read on the fd.

Dependencies and integration points: depends on xlator context from `xlator-dir.c` and the default generated-file FOPs.

Risks and edge cases: null context or type field causes unsafe access. Cached output can be stale after graph replacement.

Test signals: read type for multiple translators and verify it matches volfile/graph type.
