# sources/distributed-fs/eos/mgm/proc/admin/Vid.cc

## Purpose
`Vid.cc` implements the legacy opaque-parameter `ProcCommand::Vid()` command for virtual identity mapping administration.

## Important APIs, Types, And Functions
`ProcCommand::Vid()` dispatches by `mSubCmd` and calls `Vid::Ls()`, `Vid::Set()`, or `Vid::Rm()` with the opaque request environment and inherited reply fields.

## Control Flow
`ls` is allowed for the caller and sets `mDoSort` after delegating to `Vid::Ls()`. `set` and `rm` require uid 0; root requests call the corresponding `Vid` static method, while non-root requests return `EPERM`. Unknown subcommands fall through and return `SFS_OK` without setting an explicit error in this file.

## State, Persistence, And Dependencies
The persistent behavior is delegated to `mgm/vid/Vid.hh` APIs, which manage virtual identity mappings. This file depends on the legacy `ProcInterface`, global MGM include, and opaque request state. It mutates only inherited command output/status and sort behavior directly.

## Integration Points
This is an old proc admin command path and complements newer protobuf command classes elsewhere. It is likely reached by `vid` console operations that still use opaque key/value parameters.

## Risks
Unknown `mSubCmd` values are not rejected here, which can produce an apparently transport-successful no-op if no outer layer validates them. `ls` is not root-gated, so sensitive output control depends on `Vid::Ls()` itself. `set`/`rm` authorization is uid 0 only.

## Test Signals
Test `ls`, root and non-root `set`, root and non-root `rm`, and an unsupported subcommand. Assertions should check both command `retc` and `stdErr` because the function always returns `SFS_OK`.
