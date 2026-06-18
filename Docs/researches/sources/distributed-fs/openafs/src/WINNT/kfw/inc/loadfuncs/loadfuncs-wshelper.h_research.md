# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-wshelper.h

## Purpose

This header declares dynamic bindings for the KFW Winsock/helper DLL (`wshelp32.dll` or `wshelp64.dll`). It exposes resolver, DNS packet, Hesiod, host identity, and OS helper functions to OpenAFS Windows code.

## Important APIs, Types, and Functions

- `WSHELPER_DLL` selects `wshelp64.dll` on `_WIN64`, otherwise `wshelp32.dll`.
- Host/service lookup APIs include `rgethostbyname`, `rgethostbyaddr`, `rgetservbyname`, `gethinfobyname`, `getmxbyname`, `getrecordbyname`, `rrhost`, `wsh_gethostname`, and `wsh_getdomainname`.
- Address and OS helpers include `inet_aton`, `WhichOS`, and `WSHGetHostID`.
- Resolver APIs include `res_init`, `res_setopts`, `res_getopts`, `res_mkquery`, `res_send`, `res_querydomain`, `res_search`, `dn_comp`, and `rdn_expand`.
- Hesiod APIs include `hes_to_bind`, `hes_resolve`, `hes_error`, `hes_getmailhost`, `hes_getservbyname`, `hes_getpwnam`, and `hes_getpwuid`.

## Control Flow

Callers load `WSHELPER_DLL`, resolve the helper symbols, optionally initialize resolver state with `res_init`, and then use resolver/Hesiod calls for name, service, mailhost, passwd, DNS, and host-ID operations. The header does not implement lookup logic.

## State and Persistence Behavior

The external DLL owns resolver options and any static buffers returned by resolver/Hesiod functions. `res_setopts` and `res_getopts` imply process-local resolver state. The header itself holds only dynamically populated function pointers in consumers.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and `<wshelper.h>`, along with Winsock structs such as `hostent`, `servent`, `in_addr`, and helper structs like `rrec`, `hes_postoffice`, and `passwd`. It integrates OpenAFS/KFW with DNS and Hesiod naming services used in older MIT environments.

## Risks

- Several classic resolver APIs return pointers to static storage and are not generally thread-safe.
- DNS packet APIs require caller-provided buffers and lengths; malformed inputs can lead to truncation or parse errors.
- Hesiod and legacy resolver behavior may be unavailable in modern deployments.
- The declaration for `rgetservbyname` returns `struct servent` by value, while many resolver APIs traditionally return a pointer; call sites must match the actual DLL ABI.

## Test Signals

Tests should cover DLL load by architecture, resolver initialization, host/service lookups using controlled names, DNS query buffer sizing, and behavior when Hesiod is not configured. Static-buffer callers should be reviewed under concurrent use.
