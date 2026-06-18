<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-mailbox.h -->
# sources/distributed-fs/ceph-client/include/linux/omap-mailbox.h

## Purpose
This minimal header defines the OMAP mailbox message scalar type and a helper macro to cast arbitrary message data to a 32-bit mailbox word.

## Important APIs, types, and functions
`typedef uintptr_t mbox_msg_t` represents a mailbox message value. `omap_mbox_message(data)` casts through `mbox_msg_t` and truncates to `u32`.

## Control flow
Mailbox clients use the macro when writing a message word to OMAP mailbox hardware or APIs. There are no functions or runtime branches.

## State and persistence
No state is stored. Message persistence is hardware/mailbox-queue dependent outside this header.

## Dependencies and integration points
It integrates legacy OMAP mailbox users with interprocessor communication code. It assumes `uintptr_t`/`u32` are available via included dependencies from callers.

## Risks and test signals
Risks include pointer truncation on 64-bit builds, type visibility if included standalone, and endian/width assumptions for mailbox payloads. Test compile coverage on OMAP mailbox users and message value round trips through hardware/register APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-mailbox.h -->
