# sources/distributed-fs/coda/coda-src/scripts/pwdtopdbtool.py

Purpose: migration helper that converts legacy `/vice/db/user.coda` and `group.coda` data into commands for `pdbtool`.

Control flow: removes `/vice/db/prot_users.cdb` if present, opens a write pipe to `pdbtool`, writes default `System`, `System:Administrators`, and `System:AnyUser` identities with legacy ACL-compatible ids, reads old users as colon-separated records and emits `nui` commands, reads old groups and emits `ng`, `ci`, and `ag` commands mapping names to saved user ids, then closes the pipe.

State/persistence: deletes the protection users CDB and relies on `pdbtool` to create/update protection database state. It reads fixed `/vice/db` paths.

Dependencies, risks, tests: depends on Python 3, `pdbtool` in `PATH`, legacy file formats, and group members all appearing in `user.coda`. Risks include no error handling for missing files, unsafe pipe status ignoring, unquoted names in command language, and hardcoded owner ids. Test with sample users/groups, missing member names, existing database removal, and ACL id compatibility.
