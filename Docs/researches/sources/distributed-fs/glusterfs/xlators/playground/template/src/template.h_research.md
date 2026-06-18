# sources/distributed-fs/glusterfs/xlators/playground/template/src/template.h

## Purpose
Declares the private state, memory type IDs, and message IDs for the playground template translator.

## Important APIs, Types, And Functions
`template_private_t` contains a sample `dummy` field. `enum gf_template_mem_types_` defines the private allocation ID and end marker. `GLFS_MSGID(TEMPLATE, ...)` declares no-memory and no-graph message IDs.

## Control Flow
`template.c` uses these declarations during init, reconfigure, diagnostics, and memory accounting.

## State And Persistence
Only the in-memory `dummy` field is represented. No durable state is defined.

## Dependencies And Integration Points
Includes core Gluster headers, defaults, memory types, and message ID support. The comments explain how a real translator would split mem-types and messages into separate headers.

## Risks
Combining template, mem-type, and message declarations in one header is useful for an example but not the typical production layout. The `TEMPLATE` message component must exist in `glfs-message-id.h`.

## Test Signals
Compilation validates the message component and memory type usage. Statedump and metrics confirm `template_private_t` is populated.
