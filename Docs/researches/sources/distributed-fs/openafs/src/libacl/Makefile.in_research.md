## sources/distributed-fs/openafs/src/libacl/Makefile.in

Purpose: this makefile builds the OpenAFS ACL library and installs public ACL/right headers.

Important targets: `all` builds `liboafs_acl.la`, installs static `libacl.a`, and runs `depinstall` for `afs/acl.h`, `afs/prs_fs.h`, and component version generation. `LT_objs` are `aclprocs.lo`, `netprocs.lo`, and version object. The shared library depends on ptserver protection RPC support. `test` descends into `test`.

State and persistence: produces static/shared libraries, installed headers, generated version source, and cleaned object/library files.

Dependencies and integration points: includes config, LWP, and lwptool make fragments; links with ptserver protection library for name/ID translation in ACL conversion.

Risks: install target puts `libacl.a` under `libdir/afs`; consumers must match that library layout. The `clean` target removes `acltest` even though the test binary is produced in a subdirectory target.

Test signals: building `libacl.a`/`liboafs_acl.la` and running `make test` in `libacl/test`.
