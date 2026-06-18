# sources/distributed-fs/ceph-client/security/selinux/ss/policydb.c

## Purpose
`policydb.c` implements the SELinux binary policy database reader, writer, validator, index builder, and destructor. It turns a policy image into the in-kernel `struct policydb` model used by `services.c`: symbol tables, access vectors, conditional rules, class defaults, role transitions, filename transitions, object contexts, genfs rules, MLS ranges, policy capabilities, permissive domains, neveraudit domains, and type-attribute maps.

## Important APIs, Types, and Functions
The public entry points are `policydb_read()`, `policydb_write()`, `policydb_destroy()`, `policydb_load_isids()`, `policydb_context_isvalid()`, `policydb_*_isvalid()`, `policydb_filenametr_search()`, `policydb_rangetr_search()`, `policydb_roletr_search()`, `string_to_security_class()`, `string_to_av_perm()`, and `str_read()`. Major helpers include `policydb_init()`, `policydb_index()`, symbol read/write callbacks, `ocontext_read()/ocontext_write()`, `genfs_read()/genfs_write()`, `filename_trans_read()/filename_trans_write()`, and boundary sanity checks.

## Control Flow
`policydb_read()` validates magic, string, policy version, config flags, and compatibility table sizes; initializes symbol tables; reads symbols through `read_f[]`; requires the `process` class and transition permissions; loads AV tables and conditionals; reads role transitions/allows, filename transitions, indexed symbol arrays, object contexts, genfs entries, range transitions, type-attribute maps, and boundary checks. Read-side helpers validate references as they parse, so most malformed policies fail before publication. `policydb_write()` reverses this order into a bounded `policy_file`, refusing very old policy versions that the writer cannot safely encode.

## State and Persistence
State is entirely in memory after load but mirrors the binary policy layout for `security_read_policy()`. `next_entry()` and `put_entry()` advance the policy buffer and enforce length/overflow checks. `policydb_destroy()` is comprehensive: it maps over symbol tables, conditional policy, AV tables, role/filename/range hash tables, object contexts, genfs lists, and ebitmaps.

## Dependencies and Integration Points
This file depends on SELinux core structures from `avtab`, `conditional`, `mls`, `context`, `ebitmap`, `sidtab`, and `services`. `services.c` consumes policy lookup functions for class/permission mapping, SID computation, filename transitions, role transitions, range transitions, policycaps, and object-context SID lookup.

## Risks
The critical risks are binary parser regressions, version compatibility mistakes, missing cleanup on partial load failure, invalid symbol indexes, duplicate transition keys, and off-by-one errors in policy value arrays. Filename transition compatibility paths are especially sensitive because old policies are expanded into the newer compressed shape. MLS/category reads must destroy partially initialized bitmaps on failure.

## Test Signals
Useful signals include SELinux policy load/unload tests across supported policy versions; malformed/truncated policy images; duplicate genfs, role, and filename transition entries; MLS and non-MLS policy round trips through `policydb_write()`; boundary violation policies; policies with unknown classes/permissions under allow/reject modes; and KASAN/KMEMLEAK checks around failed reads.
