# sources/distributed-fs/eos/mgm/vid/Vid.hh

## Purpose
Declares the static VID administration interface for setting, listing, and removing MGM virtual identity mappings.

## Important APIs, types, and functions
`Vid` has trivial construction/destruction and static methods `Set(const char*, bool)`, `Set(XrdOucEnv&, int&, XrdOucString&, XrdOucString&, bool)`, `Ls()`, and `Rm()`.

## Control flow
Command handlers parse an XRootD environment, call the static methods, and receive return codes plus stdout/stderr strings. `storeConfig` controls whether operations update only memory or also the config engine.

## State and persistence behavior
The header owns no state. Implementation mutates `common::Mapping` globals and optionally config-engine entries.

## Dependencies and integration points
Depends on MGM namespace macros and XRootD `XrdOucString`/`XrdOucEnv`. It is consumed by admin proc command handling.

## Risks and test signals
Because this is a global static API, tests must isolate and reset `Mapping` globals. Verify wrapper methods set `retc`, `errno`, and stdout/stderr consistently on success/failure.
