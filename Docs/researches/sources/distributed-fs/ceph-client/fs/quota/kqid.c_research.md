# sources/distributed-fs/ceph-client/fs/quota/kqid.c

Purpose: Provides generic helpers for comparing, ordering, validating, and exporting kernel quota identifiers (`struct kqid`) across user, group, and project quota types.

Important APIs, types, and functions: Exports `qid_eq()`, `qid_lt()`, `from_kqid()`, `from_kqid_munged()`, and `qid_valid()`. Each function switches on `kqid.type` and delegates to uid, gid, or project-id helpers such as `uid_eq()`, `gid_lt()`, `from_kprojid()`, and `projid_valid()`.

Control flow: Equality first compares quota type, then compares the type-specific union member. Ordering sorts by type before comparing type-specific ids. Namespace conversion maps the selected id into a target `user_namespace`; the munged variant returns the overflow id instead of `(qid_t)-1` for unmapped ids. Invalid quota types trigger `BUG()`, making callers responsible for providing a valid type.

State and persistence: No persistent state is stored here. The file only transforms and validates id values passed by quota core, syscalls, and quota formats.

Dependencies and integration points: Used by dquot hashing and matching, quota tree lookup, netlink warning payload generation, quotactl user-copy paths, and any filesystem that needs type-generic quota ids. It depends on Linux id-mapping primitives and the `USRQUOTA`, `GRPQUOTA`, and `PRJQUOTA` type constants.

Risks and test signals: Key risks are invalid type propagation and namespace conversion errors that expose the wrong id to userspace. Test mixed quota-type sorting, unmapped ids in non-init namespaces, project quota ids, and all exported helpers with boundary ids.
