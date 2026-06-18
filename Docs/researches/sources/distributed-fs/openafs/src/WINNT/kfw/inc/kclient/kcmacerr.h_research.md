## sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kcmacerr.h

Purpose: Defines Macintosh Project Mandarin/KClient error constants and copied MacTCP/DNR network error constants used by legacy Kerberos client compatibility code.

Important APIs/types/functions: Declares `typedef signed short OSErr`; the anonymous enum starts Kerberos client errors at `cKrbCorruptedFile = -1024` and reserves `cKrbKerberosErrBlock = -20000`; `ipBadLapErr` through `outOfMemory` mirror MacTCP negative return codes.

Control flow: No executable logic. Consumers compare negative `OSErr` values returned from KClient-style APIs or translate them into user-facing messages.

State and persistence: No state. The only persistence contract is numeric stability of exported error values.

Dependencies and integration points: Integrates with KClient/KServer compatibility layers, MacTCP-compatible error handling, and any Windows KfW code that keeps Macintosh-era error numbers for cross-platform behavior.

Risks: The header has no include guard and defines common names such as `outOfMemory`, which can collide. `OSErr` is fixed to 16 bits while some consumers may store errors in `long`. The source contains legacy copyright text with non-ASCII bytes, so encoding-preserving edits matter.

Test signals: Compile consumers that include it more than once and alongside Windows/Kerberos headers; verify exact numeric values and sign extension when converted to wider error types; exercise translation of user-cancelled, configuration, TCP, and DNS failures.
