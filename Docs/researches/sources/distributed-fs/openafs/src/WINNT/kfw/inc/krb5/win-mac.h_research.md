## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/win-mac.h

Purpose: Windows platform ABI support header for MIT Kerberos/KfW public headers.

Important APIs/types/functions: Defines read-password dialog IDs, enforces 32-bit `time_t` compatibility on 32-bit MSVC builds when included from internal Kerberos headers, sets `SIZEOF_*`, includes `windows.h`, defines `SIZE_MAX`, declares `KRB5_CALLCONV`, `KRB5_CALLCONV_C`, and `KRB5_CALLCONV_WRONG`, supplies system typedefs such as `u_long`, `u_int`, `u_short`, and compatibility macros such as `THREEPARAMOPEN`.

Control flow: Preprocessor-only setup used before public function prototypes are emitted. Some branches are resource-compiler-only via `RES_ONLY`.

State and persistence: No runtime state. It locks ABI assumptions for time, integer sizes, and calling conventions.

Dependencies and integration points: Included by `krb5.h`, `com_err.h`, `profile.h`, and KerberosIV DES headers on Windows. It binds public declarations to KfW DLL export conventions.

Risks: Include order matters: if `time_t` has already been defined as 64-bit in 32-bit Windows builds, the header deliberately errors to prevent ABI mismatch. Global Windows includes and typedefs can collide with other portability layers.

Test signals: Compile with MSVC 32-bit and 64-bit settings, resource compiler mode, and public-header-only mode; verify calling conventions in generated import libraries and that `time_t` ABI checks fire when expected.
