# sources/distributed-fs/coda/coda-src/scripts/vice-setup-user.in

Purpose: initializes Coda protection/authentication data for the first administrative user.

Control flow: loads `server.conf`, enters `$vicedir/db`, prompts for a numeric uid other than 0 or 1 and username other than root/system, backs up existing `prot_users.cdb`, writes a temporary `pdbsetup` script defining `System`, the admin user, `System:Administrators`, and `System:AnyUser`, feeds it to `pdbtool`, removes the setup file, then creates `auth2.pw` from a temporary `passwd.coda` using `initpw` with restrictive umask and default password `changeme`.

State/persistence: modifies protection database and authentication password file in `$vicedir/db`.

Dependencies, risks, tests: depends on `pdbtool`, `initpw`, interactive input, and correct token/password conventions. Risks include default password, username not escaped in command file, old database backup overwritten by rerun, and minimal uid validation. Test uid validation, rejected usernames, backup behavior, restrictive `auth2.pw` permissions, and successful admin authentication after setup.
