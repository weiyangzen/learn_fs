# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen-messages.h

## Purpose
This header reserves a message-ID header for delay-gen but currently declares no message IDs.

## Important APIs, Types, And Functions
It includes `<glusterfs/glfs-message-id.h>` and contains the standard append-only message-ID guidance, but no `GLFS_MSGID()` list.

## Control Flow
There is no control flow.

## State And Persistence Behavior
No state is held. If IDs are added later, they become stable log identifiers and should follow append-only rules.

## Dependencies And Integration Points
It is included by `delay-gen.h`, giving the translator a conventional place for structured logging IDs if it moves from `gf_log()` to `gf_msg()`.

## Risks
Current code logs with `gf_log()` and therefore lacks structured message IDs. Future additions must not reuse IDs or reorder an introduced list.

## Test Signals
Compilation is the main signal today. Static review should catch any future `gf_msg()` use without a corresponding ID.
