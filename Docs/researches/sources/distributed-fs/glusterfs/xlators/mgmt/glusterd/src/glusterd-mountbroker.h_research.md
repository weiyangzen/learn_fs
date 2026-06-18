# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mountbroker.h

## Purpose

`glusterd-mountbroker.h` defines the data model and public functions for GlusterD mountbroker support. It is the contract between mountbroker configuration parsing/evaluation and the rest of GlusterD.

## Important APIs and types

`MB_HIVE` names the cookie directory `mb_hive` under the configured mountbroker root. `gf_setrel_t` enumerates supported set relations: `SET_SUB`, `SET_SUPER`, `SET_EQUAL`, and `SET_INTERSECT`. `gf_mount_pattern_t` stores one parsed relation: a NULL-terminated component array, the relation condition, and a boolean negation flag. `gf_mount_spec_t` stores a list node, label, array of parsed patterns, and pattern count.

The public functions are `parse_mount_pattern_desc()`, which parses a mutable descriptor string into `gf_mount_spec_t`; `make_georep_mountspec()`, which constructs a geo-replication-safe spec; and `glusterd_do_mount()`, which evaluates a labeled request dictionary and returns a cookie path for the resulting mount.

## Control flow and state contract

Callers create or populate `gf_mount_spec_t` records, parse descriptor strings into their `patterns` arrays, link specs onto `glusterd_conf_t::mount_specs`, and later call `glusterd_do_mount()` with a label and ordered argument dictionary. The header makes the ownership model implicit: parsed components and pattern arrays are dynamically allocated by the parser, and `glusterd_do_mount()` returns a dynamically allocated `*path` on success.

## Dependencies and integration points

The structs depend on Gluster list and boolean types (`struct cds_list_head`, `gf_boolean_t`) and Gluster dictionaries for request arguments. The implementation integrates with GlusterD volume state, mountbroker translator options, filesystem syscalls, and the `glusterfs` runner.

## Risks and test signals

The header has no include guard, so repeated inclusion depends on the build's existing include ordering and should be treated carefully. The parser API requires mutable descriptor strings; passing string literals would be unsafe. Tests should compile multiple consumers, validate that parsed specs remain NULL-terminated, and assert that callers free mount spec allocations and returned cookie paths through the expected Gluster allocator conventions.
