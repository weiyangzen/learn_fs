<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_message.c -->
# sources/distributed-fs/openafs/src/pam/afs_message.c

## Purpose
Provides the fallback message catalog and syslog formatter for the OpenAFS PAM module. It maps numeric `PAMAFS_*` message IDs to format strings used by auth, setcred, session, password, and prompt helpers.

## Important APIs, Types, And Functions
The file defines `fallback_messages`, `num_fallbacks`, `pam_afs_message(int msgnum, int *freeit)`, and `pam_afs_syslog(int priority, int msgid, ...)`. It uses `vsyslog`, varargs, and message constants from `afs_message.h`.

## Control Flow
`pam_afs_message` bounds-checks the message ID, falls back to index 0 for invalid values, and reports that the returned string must not be freed. `pam_afs_syslog` obtains the format string, formats varargs into syslog, and frees only if a future catalog-backed implementation requests it.

## State And Persistence
The message table is static process state. The only external side effect is syslog output.

## Dependencies And Integration Points
Every PAM source file uses these messages for consistent diagnostics and prompts through `afs_pam_msg.c`. The placeholder comment indicates this could be replaced by an NLS catalog later.

## Risks And Test Signals
Risks include format-string/signature mismatches between message IDs and callers, an apparent missing comma between message 46 and 47 strings causing concatenation, and no localization despite the abstraction. Test signals include compile warnings, exercising each message ID with representative arguments, and checking syslog output for malformed combined messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_message.c -->
