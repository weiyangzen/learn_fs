## sources/distributed-fs/openafs/src/libuafs/afsload/lib/AFS/Load/Action.pm

Purpose: Defines the afsload action framework and all built-in filesystem action classes used by configuration `node` directives.

Important APIs and classes: Base `AFS::Load::Action` provides `_interpret_impl`, `parse`, `new`, and `do`. Action packages include `chdir`, `creat`, `read`, `cat`, `cp`, `truncwrite`, `append`, `unlink`, `rename`, `hlink`, `slink`, `access_r`, `fail`, `ignore`, `mkdir`, and `rmdir`.

Control flow: `parse` maps the action name to package `AFS::Load::Action::<name>`, calls its constructor, and attaches action index. Each action validates argument count during construction. `do` delegates to `doact`. Most `doact` implementations call one or more `AFS::ukernel::uafs_*` functions and return `(0,0)` on success or `(errno_or_code, message)` on failure. `fail` wraps another action and succeeds only if it returns the expected error. `ignore` wraps another action and always succeeds.

State and persistence: Action objects store only arguments. Runtime actions mutate AFS or local filesystem state: files, directories, links, and working directory. `cp` can bridge local files and AFS depending on path form.

Dependencies and integration: Depends on POSIX constants, `AFS::ukernel`, `Errno`, and `Number::Format` for `cp` sizes. Instantiated by `AFS::Load::Config` and executed by `afsload_run.pl`.

Risks: `fail` only treats a single digit string as numeric because it uses `/^\d$/`, so multi-digit numeric errno values are interpreted as symbolic names. `cp` opens local files via two-argument `open` with interpolated paths, which is shell-like and unsafe for special characters. Some write checks use string `eq` for numeric byte counts. Error reporting relies heavily on `$!` after XS calls.

Test signals: Constructor arity checks for every action, success and failure paths for each `uafs_*` call, `fail` with symbolic and numeric errors, `ignore`, local-to-AFS and AFS-to-local `cp`, partial write/read behavior, and unsafe path handling.
