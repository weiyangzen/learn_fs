# sources/distributed-fs/openafs/src/audit/audit.h

## Purpose
`audit.h` is the public audit event and argument-type header. It gives OpenAFS servers stable event-name strings and declares the audit API.

## Important APIs, types, and functions
The header defines AUD argument tags such as `AUD_END`, `AUD_STR`, `AUD_INT`, `AUD_LST`, `AUD_HOST`, `AUD_LONG`, `AUD_DATE`, `AUD_FID`, `AUD_FIDS`, `AUD_NAME`, `AUD_ID`, `AUD_ACL`, MR-AFS residency tags, and butc tape tags. It hardcodes selected authorization error constants to avoid build cycles. It defines many event-name macros for volserver, ptserver, budb, kauth, fileserver, bosserver, vlserver, MR-AFS, remio, and tape-controller operations. Function prototypes expose audit emission, configuration, lifecycle, user-locality checks, and stats.

## Control flow
No runtime control flow exists in the header, but the AUD tags control how `audit.c` consumes variadic arguments.

## State and persistence
The header defines no state. Its event names become persistent audit log vocabulary, so changing them affects downstream log processing.

## Dependencies and integration points
It includes `<afs/cmd.h>` for command option integration and is included by audit emitters across server code as well as `audit.c`. The prototypes connect server startup option parsing, daemon open/close lifecycle, and runtime audit events.

## Risks
The large macro list is a compatibility contract; typos or renames can break external audit tooling. Hardcoded error constants can drift from `.et` definitions if upstream values ever change. The variadic API has no compile-time type checking for AUD tag/argument pairs.

## Test signals
Compile representative audit emitters, verify event names in generated logs, exercise each AUD tag through `audit.c`, and compare hardcoded error constants against generated error headers during maintenance.
