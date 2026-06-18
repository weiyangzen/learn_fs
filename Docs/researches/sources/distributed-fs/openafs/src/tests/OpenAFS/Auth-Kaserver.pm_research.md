# sources/distributed-fs/openafs/src/tests/OpenAFS/Auth-Kaserver.pm

## Purpose
`Auth-Kaserver.pm` is a small legacy Perl authentication helper for kaserver-based test cells.

## Important APIs, types, and functions
The package is `OpenAFS::Auth`. It defines `getcell`, `getrealm`, `authadmin`, and `authuser`.

## Control flow
`getcell` and `getrealm` read `ThisCell` from the configured AFS config directory, with `getrealm` uppercasing the result. `authadmin` and `authuser` execute `echo "Proceeding w/o authentication"|klog -pipe <principal>@REALM` via `system`.

## State and persistence behavior
It reads local cell configuration and obtains AFS tokens with `klog`; no Perl state persists beyond function calls.

## Dependencies and integration points
It depends on `OpenAFS::Dirpath`, `klog`, kaserver-era authentication semantics, and test harness code loading `OpenAFS::Auth`.

## Risks
The shell pipeline feeds a constant string rather than a real password, return codes are ignored, and the module is insecure/obsolete by modern Kerberos standards. Package-name reuse can conflict with `Auth.pm`.

## Test signals
Test readable/missing `ThisCell`, admin/user login command construction, `klog` failures, and compatibility only in kaserver test environments.
