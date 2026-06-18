# sources/distributed-fs/lizardfs/src/data/mfsexports.cfg

Purpose: sample master export/access-control file for `mfsmount` clients.

Important syntax: lines are `[ip range] [path] [options]`; path `/...` exports filesystem paths and `.` exports meta; options include read-only/read-write, `alldirs`, dynamic IP, group/permission behavior, `maproot`, `mapall`, cleartext/MD5 password, minimum client version, goal bounds, and trash-time bounds.

Control flow: parsed by `master/exports.cc`; matching entries authorize client sessions based on IP, version, meta flag, path, optional challenge/response password, and privilege mapping. The shipped active lines allow read-write access to `/` with `alldirs,maproot=0` and read-write meta access for all clients.

State and persistence: persistent security policy read by the master; reloadable through the daemon reload path.

Dependencies and integration: installed as a master example and referenced by `EXPORTS_FILENAME` in `mfsmaster.cfg.in`; drives `exports_check` session outputs.

Risks: the example is permissive if copied as-is, granting broad read-write and meta access from any IP. Password examples are documentation only; cleartext passwords are hashed by the parser but still visible in config.

Test signals: no direct parser test in this subset; `exports.cc` contains the implementation used by runtime auth.
