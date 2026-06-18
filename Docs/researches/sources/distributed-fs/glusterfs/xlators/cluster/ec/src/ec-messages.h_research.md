# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-messages.h

## Purpose
This header registers stable message IDs for the EC/disperse translator. The IDs back structured `gf_msg()` logging across option parsing, FOP handling, locking, self-heal, matrix/code generation, xattr handling, and read-mask parsing.

## Important APIs, Types, And Functions
The file uses `GLFS_MSGID(EC, ...)` to define many `EC_MSG_*` identifiers, including invalid configuration, no memory, lock/unlock failures, matrix and dynamic codegen failures, xattr parse failures, heal events, fop mismatches, and `EC_MSG_INVALID_READMASK`.

## Control Flow
There is no executable control flow. The key rule is append-only maintenance: new IDs must be added at the end, never removed or reused, to preserve log compatibility.

## State And Persistence Behavior
No runtime state is held. The IDs become part of log/event ABI and should be treated as persistent identifiers across releases.

## Dependencies And Integration Points
It includes `<glusterfs/glfs-message-id.h>` and is included by most EC implementation files that call `gf_msg()`.

## Risks
The main risk is accidental ID reuse or removal, which can break log parsers, diagnostic tooling, and support workflows. Another risk is adding generic messages without enough specificity, reducing operational value.

## Test Signals
Compilation validates the macro expansion. Log-oriented tests and static review should confirm new EC logs use an existing appropriate ID or append a new one without reordering the list.
