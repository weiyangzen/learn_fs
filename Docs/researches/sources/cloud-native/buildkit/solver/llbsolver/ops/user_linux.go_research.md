# sources/cloud-native/buildkit/solver/llbsolver/ops/user_linux.go

Purpose: resolves file operation chown users/groups on Linux by reading passwd/group files from provided snapshot mountables.

Important APIs/types/functions: `getReadUserFn` and `readUser`. `readUser` accepts a `pb.ChownOpt` plus optional user and group mountables and returns `*copy.User`.

Control flow: numeric user sets UID and default GID to the same value; numeric group sets GID. Named user requires a user mount, mounts it locally, resolves `/etc/passwd` under the root with `fs.RootPath`, and parses entries matching the name. Named group similarly reads `/etc/group`. Missing files or `ENOTDIR` are treated as not found rather than fatal.

State/persistence: no persistent state. Local mounters are mounted and unmounted within the function.

Dependencies/integration: used by real file backend construction in `file.go`; depends on snapshot local mounter, continuity `RootPath`, `moby/sys/user` parsers, and fsutil copy `User`.

Risks: missing mount for named lookups is fatal. Path rooting is necessary for safety. UID/GID default behavior for numeric user mirrors container copy expectations and should not be changed casually.

Test signals: file solver tests cover named chown mount selection with fakes, but this Linux parser itself is not directly tested in this subset.
