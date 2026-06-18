# sources/distributed-fs/eos/mgm/proc/user/Attr.cc

## Purpose

`Attr.cc` implements the legacy `ProcCommand::Attr()` command for listing, reading, setting, removing, and folding EOS extended attributes. It supports path and numeric id addressing, recursive operation over directories, exclusive set mode, access checks, and special validation for layout-related attributes.

## Important APIs, Types, and Functions

`SanitizeXattr()` validates `sys.forced.blocksize` and `user.forced.blocksize` by base64-decoding the value and checking `LayoutId::IsValidBlocksize()`. `ProcCommand::Attr()` handles subcommands `ls`, `get`, `set`, `rm`, and `fold`. It uses `Resolver::retrieveFileIdentifier`, `GetPathFromFid()`, `GetPathFromCid()`, `_find`, `_access`, `_attr_ls`, `_attr_get`, `_attr_set`, and `_attr_rem`.

## Control Flow

The command maps the input path or resolves `fid/fxid/pid/pxid/cid/cxid` to a canonical path, unseals XRootD paths, enters token scope, validates subcommand and required xattr parameters, strips double quotes from values, and sanitizes selected keys. Recursive option `r` uses `_find` to collect target directories, falling back to the original path for file-like results; otherwise it operates on one path. Option `c` enables exclusive creation. `set` and `rm` switch to write access mode. Each target then executes the selected branch: `ls` lists visible attributes, `set` validates user ACL and `sys.attr.link` constraints, `get` reads one key, `rm` removes one key, and `fold` removes local attributes whose values match a linked origin.

## State and Persistence

The command persists xattr changes on namespace entries. `fold` can remove local copies based on `sys.attr.link` inheritance. `set sys.attr.link` requires the referenced value to be an existing directory. Recursive operations can update or inspect many directories and return after the first fatal access or validation error in several branches.

## Dependencies and Integration Points

`Attr()` integrates with EOS access macros, token scoping, namespace path mapping, `gOFS` xattr APIs, `Path`, `Resolver`, `IView`, and layout validation. It overlaps behavior with `AclCmd` for user ACL gating but uses the older opaque command interface.

## Risks and Test Signals

Because `Attr()` is a generic xattr mutation surface, validation coverage is intentionally narrow and most keys are trusted. Recursive mode only targets directory maps produced by `_find`, with a special fallback for files. `fold` shadows `retc` with a local variable in one branch, which can obscure error handling. Test signals include id-to-path resolution, invalid identifiers, recursive file fallback, exclusive set, user ACL rejection without `sys.eval.useracl`, `sys.attr.link` target validation, blocksize base64 validation, `ls -V`, binary-ish `sys.file.buffer` display, and fold behavior with matching and non-matching link attributes.
