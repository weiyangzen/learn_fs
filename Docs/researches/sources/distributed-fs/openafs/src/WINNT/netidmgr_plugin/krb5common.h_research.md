# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/krb5common.h

## Purpose
Declares Kerberos helper APIs used by the AFS NetIDMgr plugin.

## Important APIs, Types, And Functions
Under `!NO_KRB5`, declares error handling, error-string formatting, context/cache initialization, cache lookup by identity, identity expiration inspection, and `MAX_HSTNM` fallback.

## Control Flow
No runtime control flow; conditional compilation removes declarations when Kerberos support is disabled.

## State And Persistence
No direct state. Declared functions work with caller-owned Kerberos contexts/caches and NetIDMgr identities.

## Dependencies And Integration Points
Includes `krb5.h` and expects NetIDMgr types to be visible from broader plugin headers. Implemented mostly by `krb5common.c` and consumed by AFS token acquisition code.

## Risks
The header declares `khm_krb5_get_error_string()` without a matching implementation in the researched `.c`, so linkage depends on another file or dead code. Conditional declarations can hide missing stubs in `NO_KRB5` builds.

## Test Signals
Compile/link full plugin with and without `NO_KRB5`; call cache initialization and identity lookup from token acquisition paths.
