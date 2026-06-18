<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_message.h -->
# sources/distributed-fs/openafs/src/pam/afs_message.h

## Purpose
Declares numeric message IDs and public message/syslog functions for the OpenAFS PAM module.

## Important APIs, Types, And Functions
The header defines `PAMAFS_UNKNOWNOPT` through `PAMAFS_OTHERCELL`, matching the fallback table in `afs_message.c`, and declares `pam_afs_message` and `pam_afs_syslog`.

## Control Flow
There is no runtime control flow. Consumers pass constants to message, prompt, and syslog helpers instead of hard-coded strings.

## State And Persistence
No state is stored in the header. It defines the compile-time contract for message lookup.

## Dependencies And Integration Points
It is included by all PAM implementation files and must remain aligned with `fallback_messages` indices.

## Risks And Test Signals
The main risk is drift between constants and the message array, especially because varargs callers depend on exact format placeholders. Test signals are compile coverage and runtime log/prompt checks for each defined ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_message.h -->
