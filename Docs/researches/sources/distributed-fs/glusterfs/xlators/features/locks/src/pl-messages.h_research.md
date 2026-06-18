# sources/distributed-fs/glusterfs/xlators/features/locks/src/pl-messages.h

## Purpose

`pl-messages.h` defines component message identifiers for the posix-locks translator. These IDs are used with Gluster's structured logging/message-id system and must remain stable over time.

## Important APIs, types, and functions

The file includes `<glusterfs/glfs-message-id.h>` and invokes:

`GLFS_MSGID(PL, PL_MSG_LOCK_NUMBER, PL_MSG_INODELK_CONTENTION_FAILED, PL_MSG_ENTRYLK_CONTENTION_FAILED);`

This declares the PL component's message-id symbols for lock numbering and contention-notification failures.

## Control flow

There is no runtime control flow. The macro expands at compile time into message-id definitions consumed by logging call sites.

## State and persistence behavior

There is no runtime state. The stability of these identifiers is externally significant because logs, diagnostics, and downstream tooling may rely on message IDs remaining unique and non-reused.

## Dependencies and integration points

The header depends on Gluster's global message-id infrastructure and is included by `entrylk.c`; related inodelk/entrylk contention paths can use the declared IDs for structured messages. The comments define the maintenance contract: append new IDs, do not delete or reuse old ones, and ensure the component name matches `glfs-message-id.h`.

## Risks and edge cases

Removing or reordering IDs can cause log compatibility problems. Adding IDs under the wrong component name can collide with global message-id allocation. The current file only defines a small set, so future logging additions should append rather than repurpose.

## Test signals

Build tests catch undefined message IDs or component mismatches. Log/diagnostic tests can verify contention failure paths emit the intended PL message identifiers.
