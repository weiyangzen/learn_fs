# sources/distributed-fs/ceph-client/security/tomoyo/condition.c

## Purpose

`condition.c` parses and evaluates optional TOMOYO ACL conditions. Conditions can constrain access by task credentials and PIDs, exec argc/envc, executable realpath, symlink target, path inode attributes, file type and mode bits, numeric ranges/groups, name groups, and specific `exec.argv[]`/`exec.envp[]` entries.

## Important APIs, types, and functions

`tomoyo_get_condition()` parses the condition suffix of a policy line into a shared packed `struct tomoyo_condition`. `tomoyo_condition()` evaluates a condition against a `struct tomoyo_request_info`. `tomoyo_get_attributes()` lazily snapshots inode metadata into `struct tomoyo_obj_info`. `tomoyo_del_condition()` is implemented in `gc.c`, but this file owns the allocation layout that it later frees. The global `tomoyo_condition_list` interns duplicate condition objects.

Important internal helpers include `tomoyo_scan_bprm()` for walking `linux_binprm` argv/env pages, `tomoyo_argv()` and `tomoyo_envp()` for pattern checks, `tomoyo_scan_exec_realpath()`, quoted-name parsers, argv/envp condition parsers, `tomoyo_condition_type()`, `tomoyo_commit_condition()`, and `tomoyo_get_transit_preference()` for optional exec domain transition preferences.

## Control flow

Parsing is a two-pass process. The first dry run scans space-delimited `left[!]=right` atoms, counts condition elements and trailing arrays, recognizes `grant_log`, argv/envp clauses, numeric literals, name unions, and transition preferences. It then allocates one `struct tomoyo_condition` large enough for `condition[]`, number unions, name unions, argv entries, and envp entries, restores delimiters overwritten during the dry run, and reruns to populate the packed tail. `tomoyo_commit_condition()` merges identical conditions under `tomoyo_policy_lock` and increments shared references.

Evaluation iterates each condition element. String conditions compare `exec.realpath` or `symlink.target` against a name union. Numeric conditions compute current task IDs/PIDs, binprm argc/envc, constants for file type/mode, or lazily fetched inode stats, then compare ranges, number groups, or permission-bit intersections. `exec.argv[]` and `exec.envp[]` conditions are deferred until the numeric/string pass succeeds; `tomoyo_scan_bprm()` then reads argument pages from `linux_binprm` and verifies all required positive/negative matches.

## State and persistence behavior

Conditions are persistent shared policy objects with atomic user counts. A condition may hold references to interned names, groups, and optional transition preference strings. `tomoyo_get_attributes()` caches path and parent stat data in the request-local `tomoyo_obj_info`, setting `validate_done` and `stat_valid[]`. `tomoyo_scan_bprm()` uses request-local page dumps and temporary buffers without persisting scanned argv/env data.

## Dependencies and integration points

The parser depends on `tomoyo_parse_number_union()`, `tomoyo_parse_name_union()`, `tomoyo_get_name()`, `tomoyo_get_domainname()`, `tomoyo_correct_word()`, `tomoyo_correct_path()`, and domain update code. Evaluation depends on Linux credential helpers, PID helpers, inode/dentry access, `tomoyo_realpath_from_path()`, group and name matching from `file.c`/`group.c`, and `tomoyo_dump_page()` from `domain.c`. `tomoyo_update_domain()` calls this parser when a policy line has remaining condition text.

## Risks

The packed allocation layout is fragile: count mismatches or restoration mistakes can corrupt subsequent arrays or leak references. The parser modifies the input line in place and relies on strict token grammar, so userspace grammar drift can cause rejection. Exec argument scanning truncates at `TOMOYO_EXEC_TMPSIZE - 10` and escapes bytes into TOMOYO string syntax; tests must cover long and non-printable values. Attribute conditions can fail closed when a relevant path/object is absent. Operator precedence in expressions such as symlink target comparison should be reviewed carefully because boolean negation around pointer-returning match helpers is easy to misread.

## Test signals

Strong tests include parse/render/evaluate round trips for each condition keyword, equality and deduplication tests, `grant_log` and transition preference parsing, argv/envp positive and negative matches, absent argv/envp behavior, inode metadata conditions for files/directories/devices/parents, bit-permission comparisons, numeric range overlap and number-group checks, and exec realpath/symlink target conditions.
