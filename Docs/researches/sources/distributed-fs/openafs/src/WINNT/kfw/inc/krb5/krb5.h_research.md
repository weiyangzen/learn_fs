## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/krb5.h

Purpose: Backward-compatible forwarding header for software that still includes `<krb5.h>` from the old install location.

Important APIs/types/functions: Contains only a comment explaining the header move and `#include <krb5/krb5.h>`.

Control flow: Preprocessor forwarding only.

State and persistence: None.

Dependencies and integration points: Depends on include paths resolving `krb5/krb5.h` to the real MIT Kerberos public header. It preserves source compatibility for older OpenAFS/KfW consumers.

Risks: Include-path ordering can accidentally pick another `krb5/krb5.h`. Because this file has no guard of its own, it relies on the real header's guard.

Test signals: Compile legacy `#include <krb5.h>` consumers and verify they receive the same declarations as direct `#include <krb5/krb5.h>` users.
