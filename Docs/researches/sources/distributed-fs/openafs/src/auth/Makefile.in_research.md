# sources/distributed-fs/openafs/src/auth/Makefile.in

## Purpose
This makefile builds the OpenAFS authentication libraries, generated headers, XDR token code, and the `setkey` utility.

## Important APIs, types, and functions
Primary object groups are `BASE_objs`, `LT_objs`, and `KRB_objs`. Outputs include `libauth.a`, `libauth.krb.a`, `liboafs_auth.la`, `liboafs_auth_krb.la`, `libauth_pic.la`, `libpam_auth.la`, installed headers, generated `auth.h`, `cellconfig.h`, `token.h`, and generated XDR C files. `setkey` links against rxkad, afsrfc3961, rx, sys, lwp, and util libraries.

## Control flow
The `all` target builds shared/static/PIC/PAM auth variants and runs `depinstall`. Error-table inputs generate C and headers through `COMPILE_ET_C/H`. `token.xg` is processed by `RXGEN` for normal and kernel XDR variants. Special rules compile `ktc.krb.lo` with `AFS_KERBEROS_ENV` and `authcon.lo` with nodeprecated declarations. `install` and `dest` copy libraries and headers; `test` delegates into `test`; `clean` removes generated artifacts.

## State and persistence
Generated files are written into the build tree and installed include/lib directories. The makefile defines how public headers are generated from `.p.h` templates plus error tables.

## Dependencies and integration points
The auth library depends on opr, comerr, rx, rxkad, audit, util, sys, and optionally rxgk. It builds core modules including `cellconfig`, `keys`, `userok`, `authcon`, `ktc`, `token`, `realms`, and `netrestrict`. Other OpenAFS components consume these libraries for cell config, token, key, and security object handling.

## Risks
Generated header ordering matters: sources depend on `cellconfig.h` and `auth.h` produced from templates. Optional rxgk substitution changes link dependencies. Multiple object variants from the same `ktc.c` must stay compiler-flag isolated. Build/install drift could expose stale generated headers.

## Test signals
Run full build, generated target, install/dest, clean/rebuild, `make test`, rxgk-enabled and disabled configurations, Kerberos-enabled `libauth.krb.a`, and out-of-tree builds.
