## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/osconf.h

Purpose: Selects the appropriate Kerberos IV platform configuration header based on CPU, OS, and compiler macros.

Important APIs/types/functions: Defines `PC` for IBM PC, DOS, OS/2, and `_WIN32`; includes one platform header from a cascade such as `conf-bsdtahoe.h`, `conf-bsdvax.h`, `conf-bsdsparc.h`, or `conf-pc.h`.

Control flow: Preprocessor routing only. For this OpenAFS Windows tree, `_WIN32` leads to `conf-pc.h`, which establishes `WINDOWS`, `BITS32`, and `LSBFIRST`.

State and persistence: No runtime state. It determines compile-time ABI and portability assumptions for all K4 code.

Dependencies and integration points: Included by `conf.h`; downstream K4 DES and Kerberos headers depend on the selected platform definitions.

Risks: The nested macro cascade is old and incomplete for modern platforms. If no platform branch matches, `conf.h` later fails with missing byte-order/bitness errors. A wrong branch can silently set incompatible integer or calling-convention assumptions.

Test signals: Preprocessor tests for `_WIN32` selecting `conf-pc.h`; negative tests for unsupported platform macros; compile DES/KRB headers after routing.
