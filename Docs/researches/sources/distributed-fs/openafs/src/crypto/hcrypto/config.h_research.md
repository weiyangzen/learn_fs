# sources/distributed-fs/openafs/src/crypto/hcrypto/config.h

This userspace hcrypto config shim adapts Heimdal code to OpenAFS. It includes `afsconfig.h`, `afs/param.h`, optional `stdint.h`, normalizes `inline` for older compilers, renames several hcrypto symbols to `_oafs_h_*`, and defines `RETSIGTYPE`/`SIGRETURN`.

The important API is preprocessor behavior: compiler compatibility for `inline`, namespace isolation for Camellia and ENGINE functions, and signal-return compatibility expected by Heimdal-derived files. There is no runtime control flow or persistence.

Dependencies are OpenAFS platform config and compiler feature macros. Integration is all userspace hcrypto compilation units that include `<config.h>`. Risks are incomplete symbol renaming causing clashes with system OpenSSL/Heimdal, and compiler-specific `inline` substitutions changing optimization or linkage. Test signals are warning-free builds on NT, HPUX, AIX, SGI, NetBSD, and normal Unix, plus link tests with external crypto libraries present.
