# sources/distributed-fs/ceph-client/tools/perf/util/btf.c

## sources/distributed-fs/ceph-client/tools/perf/util/btf.c

Purpose: this file provides a small BTF utility for finding a struct member by name.

Important API: `__btf_type__find_member_by_name(struct btf *btf, int type_id, const char *member_name)` returns a pointer to the matching `struct btf_member` or null.

Control flow: it retrieves the BTF type by id, iterates `btf_members(t)` for `btf_vlen(t)` entries, resolves each member name offset with `btf__name_by_offset()`, and compares with `strcmp()`.

State and persistence: stateless; it returns a pointer into libbpf-owned BTF data.

Dependencies and integration: depends on libbpf BTF APIs and is declared in `util/btf.h`. Callers must ensure `type_id` names a type with members.

Risks: there is no null check for `btf__type_by_id()` before calling `btf_members(t)`, so invalid ids or non-aggregate types can crash. Member-name lookup assumes strings are non-null.

Test signals: test valid structs, missing members, invalid type ids, and non-struct type ids; consider adding defensive checks if wider callers are introduced.
