# sources/distributed-fs/lizardfs/src/master/exports.cc

Purpose: parses `mfsexports.cfg`, stores export records, serializes them for info queries, and authorizes client sessions.

Important APIs/functions: public `exports_info_size`, `exports_info_data`, `exports_check`, `exports_init`; internal parsers `exports_parsenet`, `exports_parsegoal`, `exports_parsetime`, `exports_parseversion`, `exports_parseuidgid`, `exports_parseoptions`, `exports_parseline`; load/reload/destruct helpers.

Control flow: initialization loads `EXPORTS_FILENAME`, parsing non-comment lines into a linked list of export records. `exports_check` normalizes requested path/meta mode, scans matching records by IP/version/path/password, verifies challenge-response MD5 when needed, chooses the most privileged/specific acceptable record, and returns session flags, UID/GID mapping, goal bounds, and trash-time bounds. Reload attempts to replace records atomically enough that parse failures keep old exports.

State and persistence: in-memory linked list `exports_records` and configured filename; source of truth is the exports config file. Records include path bytes, IP range, min version, password digest, flags, goal/trash limits, and UID/GID mappings.

Dependencies and integration: depends on config, event loop reload/destruct, MD5, goal ID validation, protocol session flags, user/group lookup, and logging. Called by master client authentication/session setup.

Risks: permissive configs grant broad access. Parser is C-style and mutates line buffers; malformed but nonfatal unknown options are ignored with warnings. Password digest uses MD5 challenge-response, which is legacy-grade security. `exports_info_data` must match serialized size calculations exactly.

Test signals: no direct tests in this subset; behavior can be validated through mount authentication and config parser tests.
