# sources/distributed-fs/openafs/src/auth/authcon.h

## Purpose
`authcon.h` declares internal auth-connection helpers that are not part of the external OpenAFS API.

## Important APIs, types, and functions
It defines `struct afsconf_bsso_info`, carrying an `afsconf_dir *` and optional logger callback for server-security-object construction. It declares `afsconf_BuildServerSecurityObjects_int`.

## Control flow
No runtime control flow is present.

## State and persistence
No state is stored. The struct passes context and logging behavior into `authcon.c`.

## Dependencies and integration points
It includes `<afs/cellconfig.h>` and is used by in-tree callers that want the enhanced server-security-object builder with logging. The older public wrapper still exists in `authcon.c`.

## Risks
The logger uses printf-style varargs but the type cannot enforce format correctness. The header is explicitly internal, so external consumers should not rely on ABI stability.

## Test signals
Compile in-tree callers and verify logged warnings from `afsconf_BuildServerSecurityObjects_int` with and without logger callbacks.
