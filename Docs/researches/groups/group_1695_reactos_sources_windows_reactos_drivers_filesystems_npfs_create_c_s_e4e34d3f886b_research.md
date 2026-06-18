# Group Research: ReactOS NPFS and NTFS Attribute Files

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/create.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/create.c

## Purpose
Implements NPFS create/open handling for the named-pipe filesystem, including opening the filesystem object/root directory, creating server pipe instances, opening client ends, resolving aliases, enforcing security/share rules, and waking deferred wait/notify IRPs.

## Main Responsibilities
- `NpFsdCreate` handles normal `IRP_MJ_CREATE` opens:
  - Opens `\Device\NamedPipe` itself when no name is supplied.
  - Opens the root DCB for `\`.
  - Translates aliases through `NpTranslateAlias`.
  - Uses `NpFindPrefix`/`NpFindRelativePrefix` to locate an existing FCB.
  - Connects a client to a listening server-side CCB with `NpCreateClientEnd`.
- `NpFsdCreateNamedPipe` handles `IRP_MJ_CREATE_NAMED_PIPE`:
  - Locates an existing pipe FCB or creates a new one under the root DCB.
  - Creates a server-side CCB in `FILE_PIPE_LISTENING_STATE`.
- `NpCreateClientEnd`:
  - Performs `SeAccessCheck` against the FCB security descriptor.
  - Rejects access incompatible with inbound/outbound pipe configuration.
  - Finds a listening CCB and moves it to connected state.
  - Initializes client impersonation/security state.
- `NpCreateExistingNamedPipe`:
  - Validates access, instance limits, create disposition, and share mode.
  - Adds another server instance for an existing named pipe.
  - Cancels `FSCTL_PIPE_WAIT` waiters via `NpCancelWaiter`.
- `NpCreateNewNamedPipe`:
  - Validates timeout, max instances, share mode, and byte/message mode combinations.
  - Allocates an FCB/CCB and assigns/logs a security descriptor.
- `NpTranslateAlias`:
  - Uses global alias lists built by `main.c`.
  - Upcases pipe names and substitutes matching target names.

## Important Interactions
- Depends on `strucsup.c` for FCB/CCB/root allocation and deletion.
- Depends on `prefxsup.c` for prefix matching.
- Depends on `statesup.c` for state transitions to connected/listening.
- Depends on `secursup.c` and `seinfo.c` conventions for security descriptors and client contexts.
- Uses the common NPFS deferred completion pattern: collect IRPs on `DeferredList`, release the VCB lock, then call `NpCompleteDeferredIrps`.

## Notable Behavior
- The VCB lock is acquired exclusively for all create operations because prefix tables, FCB lists, CCB lists, and waiter/notify queues can change.
- Server create derives pipe direction from share access:
  - read+write share => full duplex
  - read share => outbound
  - write share => inbound
- New named pipes require a specified negative timeout and nonzero max instance count.
- Client opens fail with `STATUS_PIPE_NOT_AVAILABLE` when no CCB is listening.

## Risks / Review Notes
- `NpCheckForNotify` contains `ASSERT(IsListEmpty(ListHead))` immediately before looping while the list is non-empty. That assertion appears contradictory if notify IRPs are expected to be completed.
- Alias translation mutates the local `FileName` copy, not the file object name itself, which is intentional for lookup but important for later diagnostics.
- Existing-pipe create requires exact share access matching the pipe configuration; this is strict and should be compared with Windows behavior if compatibility issues appear.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/datasup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/datasup.c

## Purpose
Implements NPFS data queue management. Each CCB owns inbound and outbound `NP_DATA_QUEUE` objects that hold queued reads, queued writes, buffered payloads, unbuffered IRPs, and special marker entries.

## Main Responsibilities
- `NpInitializeDataQueue` / `NpUninitializeDataQueue` set up and tear down queue state.
- `NpAddDataQueueEntry` inserts read or write entries:
  - Supports `Buffered`, `Unbuffered`, and internal special types `2` and `3`.
  - Captures client security context for write entries when needed.
  - Copies buffered write data into the queue entry allocation.
  - Marks pending IRPs and installs `NpCancelDataQueueIrp`.
- `NpRemoveDataQueueEntry` removes the head entry, updates byte/quota counters, releases security context, and handles cancellation races.
- `NpGetNextRealDataQueueEntry` skips special queue-marker entries and completes their IRPs.
- `NpCompleteStalledWrites` grants newly freed quota to previously queued buffered writes and completes write IRPs once their full quota is available.
- `NpCancelDataQueueIrp` removes a canceled IRP from its queue under the VCB lock, repairs counters, frees context, and completes cancellation.

## Queue Model
A queue is always in one of three states:
- `Empty`
- `ReadEntries`
- `WriteEntries`

The code asserts that new entries only join an empty queue or a queue already containing the same side of operation. This is the core invariant used by read/write/fsctl paths.

## Important Interactions
- Read path calls `NpAddDataQueueEntry(... ReadEntries ...)` when no data is available.
- Write path calls `NpAddDataQueueEntry(... WriteEntries ...)` when data cannot be fully delivered.
- `readsup.c` and `writesup.c` call `NpRemoveDataQueueEntry` and `NpCompleteStalledWrites`.
- `statesup.c` drains queues during disconnect/close transitions.
- Security context handoff is coordinated with `secursup.c`.

## Risks / Review Notes
- `NpAddDataQueueEntry` uses special numeric entry types `2` and `3` without named enum values, making flush/internal semantics harder to audit.
- The buffered-entry quota logic sets `HasSpace = TRUE` when quota is insufficient; the name is counterintuitive and should be read carefully.
- The cancel path must be kept consistent with all queue counter updates; it is central to avoiding stale pending IRPs and quota leaks.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/datasup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/fileinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/fileinfo.c

## Purpose
Implements query/set file information for NPFS pipe file objects. Most information is synthetic because named pipes do not map to normal disk files.

## Main Responsibilities
- `NpFsdSetInformation` dispatches set-info requests under the exclusive VCB lock.
- `NpSetBasicInfo` accepts basic-info changes but performs no work.
- `NpSetPipeInfo` changes per-end read mode and completion mode:
  - Rejects message read mode for byte-stream pipes.
  - Rejects switching to complete-operation mode in some busy queue states.
  - Notifies directory watchers through `NpCheckForNotify`.
- `NpFsdQueryInformation` dispatches query-info requests under the shared VCB lock.
- Query helpers provide:
  - `FileBasicInformation`: normal attributes.
  - `FileStandardInformation`: quota allocation and readable byte count.
  - `FileNameInformation`: root or pipe full name.
  - `FilePositionInformation`: readable byte count as current offset.
  - `FilePipeLocalInformation`: pipe type, configuration, quotas, state, end, available bytes.
  - `FilePipeInformation`: read/completion modes.
  - `FileInternalInformation` and `FileEaInformation`: zeroed placeholders.
  - `FileAllInformation`: composed from several helper outputs.

## Important Interactions
- Uses `NpDecodeFileObject` to distinguish CCB/root handles.
- Reads data queue state directly to compute available data and quota.
- Mode updates affect `read.c`, `write.c`, `readsup.c`, `writesup.c`, and `fsctrl.c`.

## Risks / Review Notes
- `NpQueryPipeLocalInfo` has an asymmetric client-end quota calculation: client `WriteQuotaAvailable` uses `OutQueue->Quota - InQueue->QuotaUsed`. Given client writes target the inbound queue, this deserves review.
- Length handling subtracts structure sizes from an unsigned `ULONG`; callers must provide valid buffer lengths or underflow risk depends on I/O manager validation.
- `FileAllInformation` intentionally omits or skips several standard substructures by subtracting access/mode/alignment sizes rather than filling them.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/fileobsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/fileobsup.c

## Purpose
Provides NPFS file-object encoding and decoding helpers. These functions map Windows `FILE_OBJECT` fields to NPFS VCB/DCB/CCB contexts and named-pipe end identity.

## Main Responsibilities
- `NpDecodeFileObject`:
  - Reads `FileObject->FsContext`.
  - Decodes the low bit as named-pipe end when present.
  - Returns node type for VCB, root DCB, or CCB.
  - Returns primary context and CCB/root CCB as requested.
- `NpSetFileObject`:
  - Stores primary context in `FsContext`.
  - Stores secondary CCB context in `FsContext2`.
  - Marks pipe file objects with `FO_NAMED_PIPE`.
  - Encodes server end by setting the low bit on a CCB pointer.
  - Sets `PrivateCacheMap` to `(PVOID)1`.

## Important Interactions
- Used by nearly every dispatch path to recover NPFS state from `FILE_OBJECT`.
- Server/client end encoding is consumed by read/write/fsctl/state transitions.
- Root DCB handles store the root DCB in `FsContext` and root CCB in `FsContext2`.

## Risks / Review Notes
- Pointer low-bit tagging assumes all CCB pointers are at least 2-byte aligned, which is true for pool allocations but is a critical invariant.
- `NpDecodeFileObject` writes `*Ccb` unconditionally in recognized cases; callers must pass a valid CCB output pointer.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/fileobsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/flushbuf.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/flushbuf.c

## Purpose
Implements `IRP_MJ_FLUSH_BUFFERS` for named pipes.

## Main Responsibilities
- `NpCommonFlushBuffers`:
  - Decodes the file object and validates it is a CCB.
  - Locks the nonpaged CCB resource.
  - Selects the opposite-direction write queue for the current pipe end.
  - If the queue contains write entries, inserts a special queue entry of type `2` with zero data size so the flush can pend behind existing writes.
  - Otherwise completes immediately with success.
- `NpFsdFlushBuffers`:
  - Wraps the common helper in filesystem entry/exit and shared VCB locking.
  - Completes the IRP unless the operation pended.

## Important Interactions
- Special queue entry type `2` is handled by `datasup.c` as a non-real queue entry that can later be skipped/completed by `NpGetNextRealDataQueueEntry`.
- Flush behavior depends on the write queue draining through reads.

## Risks / Review Notes
- The special entry type is not named in the enum, so behavior is implicit across `flushbuf.c` and `datasup.c`.
- Flush does not force delivery; it waits only when existing write entries are queued.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/flushbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/fsctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/fsctrl.c

## Purpose
Implements NPFS filesystem-control operations, including pipe listen/disconnect, peek, transceive, wait, impersonation, and client-process metadata.

## Main Responsibilities
- Unimplemented internal/event controls:
  - `NpInternalTransceive`
  - `NpInternalRead`
  - `NpInternalWrite`
  - `NpAssignEvent`
  - `NpQueryEvent`
- Client process metadata:
  - `NpQueryClientProcess` reports `Ccb->ClientSession` or `Ccb->Process`.
  - `NpSetClientProcess` is restricted to kernel callers and replaces the CCB client-session blob.
- Pipe controls:
  - `NpImpersonate` impersonates the client from the server end.
  - `NpDisconnect` server-only disconnects a pipe and clears security.
  - `NpListen` server-only transitions to listening or queues the listen IRP.
  - `NpPeek` reports pipe state, bytes available, message count/length, and optionally copies queued data without consuming it.
  - `NpTransceive` writes a message and then queues the same IRP as a read for the response.
  - `NpWaitForNamedPipe` waits on the root handle until a named pipe has a listening instance.
- `NpCommonFileSystemControl` dispatches FSCTLs and chooses shared vs exclusive VCB locking.
- `NpFsdFileSystemControl` wraps dispatch in `FsRtlEnterFileSystem` and completes non-pending IRPs.

## Important Interactions
- Uses read/write queue helpers for peek and transceive.
- Uses `statesup.c` for listen/disconnect transitions.
- Uses `waitsup.c` for `FSCTL_PIPE_WAIT`.
- Uses `secursup.c` for server-side impersonation.
- Uses event-buffer fields, but actual event assignment/query and generic-table callbacks are not implemented elsewhere.

## Notable Behavior
- `NpTransceive` requires a connected full-duplex pipe and message read mode.
- `NpWaitForNamedPipe` currently has alias translation commented out.
- `NpPeek` allows peeking a closing pipe only if queued write data remains.

## Risks / Review Notes
- Several FSCTLs return `STATUS_NOT_IMPLEMENTED`; this is a major compatibility gap.
- `NpSetClientProcess` allocates `ClientSession` but does not check allocation failure before copying.
- `NpTransceive` allocates a secondary IRP for partially written input; error paths around allocated buffers and queued IRPs are sensitive.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/fsctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/main.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/main.c

## Purpose
Initializes the NPFS driver, device object, dispatch table, fast I/O table, VCB/root DCB, and registry-configured pipe aliases.

## Main Responsibilities
- Defines globals:
  - `NpfsDeviceObject`
  - `NpAliases`
  - `NpAliasList`
  - `NpAliasListByLength`
  - `NpFastIoDispatch`
- Alias support:
  - `NpReadAlias` is an `RtlQueryRegistryValues` callback used twice: first for sizing, then for populating target-name and alias records.
  - `NpCompareAliasNames` performs length-sensitive uppercase lexical comparison.
  - `NpInitializeAliases` reads `Services\Npfs\Aliases`, builds contiguous alias storage, and inserts aliases into sorted linked lists, with short lengths indexed separately.
- `NpFsdDirectoryControl` is unimplemented.
- `DriverEntry`:
  - Initializes aliases.
  - Registers major dispatch routines for create, named-pipe create, close, read/write, information, cleanup, flush, directory control, fsctl, security, and volume info.
  - Installs fast read/write.
  - Creates `\Device\NamedPipe`.
  - Stores the VCB in the device extension and creates the root DCB.

## Important Interactions
- Alias lists are consumed by `create.c`.
- Fast I/O dispatch points to `read.c` and `write.c`.
- VCB initialization and root DCB creation are implemented in `strucsup.c`.

## Risks / Review Notes
- Directory control is explicitly unimplemented.
- Alias storage is one contiguous allocation containing `UNICODE_STRING`, `NPFS_ALIAS`, and string payloads; pointer arithmetic correctness is important.
- On `IoCreateDevice` failure after alias initialization, alias memory is not freed.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/npfs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/npfs.h

## Purpose
Central NPFS private header. Defines node types, queue structures, VCB/DCB/FCB/CCB layouts, alias structures, locking helpers, deferred completion helper, and all internal function prototypes.

## Main Structures
- `NP_VCB`:
  - Global volume/device state.
  - Holds root DCB, prefix table, VCB resource lock, event table, and wait queue.
- `NP_DCB`:
  - Directory control block, currently root-focused.
  - Holds notify lists and child FCB list.
- `NP_FCB`:
  - Named pipe file control block.
  - Holds instance counts, pipe configuration/type, default timeout, CCB list, and security descriptor.
- `NP_CCB`:
  - Per pipe instance.
  - Holds state, read/completion mode per end, file objects per end, process/session metadata, nonpaged CCB, inbound/outbound queues, client security context, and listen IRP list.
- `NP_NONPAGED_CCB`:
  - Per-instance nonpaged lock and event-buffer pointers.
- `NP_DATA_QUEUE` / `NP_DATA_QUEUE_ENTRY`:
  - Queue state and queued read/write/data entries.
- `NP_WAIT_QUEUE` / `NP_WAIT_QUEUE_ENTRY`:
  - Global wait-for-pipe support with spinlock, timer, DPC, and IRP linkage.
- Alias structures:
  - `NPFS_ALIAS`
  - `NPFS_QUERY_VALUE_CONTEXT`

## Helper Patterns
- `NpAcquireSharedVcb`, `NpAcquireExclusiveVcb`, `NpReleaseVcb` wrap the global VCB `ERESOURCE`.
- `NpCompleteDeferredIrps` completes IRPs collected while locks were held, after the caller releases the VCB lock but remains inside the filesystem critical region.
- `NpBugCheck` embeds per-file source IDs into `NPFS_FILE_SYSTEM` bugchecks.

## Important Interactions
This header ties together the complete NPFS module set: create/open, state transitions, queue operations, wait support, security, read/write, fsctl, file/volume information, and structure allocation.

## Risks / Review Notes
- Queue entry types only name `Buffered` and `Unbuffered`, but implementation uses additional numeric values.
- The event table is declared in the VCB, but backing callbacks are stubbed in `strucsup.c`.
- `PNP_ROOT_DCB_FCB` appears as a typedef name for `NP_ROOT_DCB_CCB`, which is confusing but used consistently.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/npfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/prefxsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/prefxsup.c

## Purpose
Provides prefix-table lookup helpers for resolving absolute and root-relative pipe names.

## Main Responsibilities
- `NpFindPrefix`:
  - Calls `RtlFindUnicodePrefix` on `NpVcb->PrefixTable`.
  - Returns the containing FCB/DCB by using the shared `PrefixTableEntry` field layout.
  - Computes the unmatched suffix in `Prefix`, skipping a leading separator.
- `NpFindRelativePrefix`:
  - Builds a temporary absolute name by prepending `\` to a relative name.
  - Calls `NpFindPrefix`.
  - Rewrites `Prefix->Buffer` back to point into the original relative name.
  - Returns the found FCB.

## Important Interactions
- Used by create/open paths and wait handling.
- Depends on `NP_FCB` and `NP_DCB` sharing the same `PrefixTableEntry` offset, asserted in `npfs.h`.

## Risks / Review Notes
- `NpFindPrefix` bugchecks if no prefix entry is found, so callers expect at least the root DCB prefix to always exist.
- `NpFindRelativePrefix` allocates a temporary name and relies on careful pointer recalculation after freeing it.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/prefxsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/read.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/read.c

## Purpose
Implements normal and fast read handling for named pipes.

## Main Responsibilities
- `NpCommonRead`:
  - Decodes the file object and validates CCB state.
  - Rejects invalid read direction based on pipe configuration.
  - Selects inbound or outbound queue based on pipe end.
  - If queued writes exist, drains them through `NpReadDataQueue`.
  - If pipe is closing, returns `STATUS_PIPE_BROKEN`.
  - If complete-operation mode and no data, returns `STATUS_PIPE_EMPTY`.
  - Otherwise queues the read IRP as a `ReadEntries` buffered entry.
  - Signals assigned event buffer when present.
- `NpFsdRead`:
  - Uses shared VCB lock.
  - Completes the IRP unless pending.
- `NpFastRead`:
  - Calls `NpCommonRead` without an IRP.
  - Returns `FALSE` when the fast path cannot complete synchronously.

## Important Interactions
- Uses `NpDecodeFileObject`, per-CCB nonpaged resource lock, and `NpReadDataQueue`.
- Queued reads are later satisfied by `writesup.c`.
- Fast-read counters track true/false results.

## Risks / Review Notes
- Fast read cannot pend; if data is unavailable and the operation would need queuing, it returns false for fallback.
- Event-buffer signaling is present but event assignment/query support is unimplemented in `fsctrl.c`/`strucsup.c`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/readsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/readsup.c

## Purpose
Implements copying data out of a pipe data queue for reads and peeks.

## Main Responsibilities
- `NpReadDataQueue`:
  - Reads from queued write entries into a caller buffer.
  - Supports peek mode without consuming entries.
  - Supports read-overflow behavior by forcing peek semantics.
  - Handles message-mode buffer overflow by returning `STATUS_BUFFER_OVERFLOW`.
  - Updates `QuotaInEntry`, `QuotaUsed`, and `ByteOffset` for consuming reads.
  - Transfers client security context from the data entry to the CCB.
  - Completes source write IRPs when data entries are fully consumed.
  - Calls `NpCompleteStalledWrites` after freeing quota.

## Important Interactions
- Called by `read.c` for real reads and `fsctrl.c` for peeks.
- Uses `NpGetNextRealDataQueueEntry` and `NpRemoveDataQueueEntry` from `datasup.c`.
- Uses `NpCopyClientContext` from `secursup.c`.

## Risks / Review Notes
- Exception handler around `RtlCopyMemory` contains `ASSERT(FALSE)` but does not set an error status; behavior after copy faults depends on build/assert handling.
- Message mode and overflow mode interact subtly: partial message reads surface `STATUS_BUFFER_OVERFLOW` while byte mode continues across entries.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/readsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/secursup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/secursup.c

## Purpose
Manages per-CCB client security contexts and impersonation support.

## Main Responsibilities
- `NpImpersonateClientContext` impersonates the stored client context or returns `STATUS_CANNOT_IMPERSONATE`.
- `NpFreeClientSecurityContext` dereferences the client token and frees the context allocation.
- `NpCopyClientContext` moves a data-queue-entry client context into the CCB.
- `NpUninitializeSecurity` frees and clears `Ccb->ClientContext`.
- `NpInitializeSecurity` stores client QoS:
  - Defaults to dynamic tracking, impersonation level, effective-only.
  - For dynamic tracking, does not capture a token immediately.
  - For static tracking, allocates and creates a client security context.
- `NpGetClientSecurityContext` captures a dynamic client context for client-end writes when required.

## Important Interactions
- Create path initializes security when a client connects.
- Write queue entries can carry client context for later server impersonation.
- Read path copies the writer context to the CCB when data is consumed.
- FSCTL impersonation uses the current CCB context.

## Risks / Review Notes
- Correct ownership transfer is subtle: queue entries may own a context until `NpCopyClientContext` moves it to the CCB.
- Dynamic tracking intentionally delays capture until write time for client-originated writes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/secursup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/seinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/seinfo.c

## Purpose
Implements query/set security information for named-pipe FCB security descriptors.

## Main Responsibilities
- `NpCommonQuerySecurityInfo`:
  - Validates CCB handle.
  - Calls `SeQuerySecurityDescriptorInfo` against `Fcb->SecurityDescriptor`.
  - Converts `STATUS_BUFFER_TOO_SMALL` to `STATUS_BUFFER_OVERFLOW` and reports required length.
- `NpCommonSetSecurityInfo`:
  - Validates CCB handle.
  - Builds a modified descriptor with `SeSetSecurityDescriptorInfo`.
  - Logs/caches it with `ObLogSecurityDescriptor`.
  - Replaces `Fcb->SecurityDescriptor` and dereferences the old descriptor.
- `NpFsdQuerySecurityInfo` and `NpFsdSetSecurityInfo` wrap common helpers under exclusive VCB locking.

## Important Interactions
- Security descriptors are assigned for new pipes in `create.c`.
- Access checks for opens use the FCB security descriptor in `create.c`.

## Risks / Review Notes
- Query and set both take the exclusive VCB lock, which is conservative.
- Set path assumes `SeSetSecurityDescriptorInfo` returns a descriptor distinct from the old one, asserted in code.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/seinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/statesup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/statesup.c

## Purpose
Implements named-pipe state transitions: listening, connected, disconnected, closing, and close cleanup behavior.

## Main Responsibilities
- `NpCancelListeningQueueIrp` cancels a pending listen IRP.
- `NpSetConnectedPipeState`:
  - Converts a listening CCB to connected.
  - Sets default client read/completion modes.
  - Binds the client file object.
  - Completes queued listen IRPs successfully.
- `NpSetDisconnectedPipeState`:
  - Handles transitions from disconnected/listening/connected/closing.
  - Drains queues with `STATUS_PIPE_DISCONNECTED`.
  - Clears client event buffer, client file object, security, and client session.
- `NpSetListeningPipeState`:
  - Cancels waiters for newly available pipe instances.
  - Returns `STATUS_PIPE_LISTENING` in complete-operation mode.
  - Otherwise queues the listen IRP pending cancellation/connection.
- `NpSetClosingPipeState`:
  - Handles final close for server or client ends.
  - Drains affected queues with `STATUS_PIPE_BROKEN`.
  - Clears file objects.
  - Deletes CCB and possibly FCB when no instances remain.
  - Signals event buffers on connected-to-closing transition.

## Important Interactions
- Called by create, fsctl listen/disconnect, cleanup/close paths outside this group, and queue support.
- Uses `NpDeleteCcb`, `NpDeleteFcb`, `NpRemoveDataQueueEntry`, and wait cancellation.

## Risks / Review Notes
- Switch fallthroughs are intentional and documented by comments; changes here require care.
- Event-buffer deletion depends on event-table support, which is stubbed in `strucsup.c`.
- Closing state drains only selected queues depending on which pipe end closes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/statesup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/strucsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/strucsup.c

## Purpose
Allocates, initializes, and deletes NPFS core structures: VCB, root DCB, FCBs, CCBs, root DCB CCBs, and event-table entries.

## Main Responsibilities
- Globals:
  - `NpRootDCBName`
  - `NpVcb`
- Event-table callbacks:
  - `NpEventTableCompareRoutine`
  - `NpEventTableAllocate`
  - `NpEventTableDeallocate`
  - These are unimplemented.
- `NpDeleteEventTableEntry` dereferences an event and deletes the table element.
- `NpInitializeVcb` zeroes VCB, initializes prefix table, resource, generic event table, and wait queue.
- `NpCreateRootDcb` allocates root DCB, initializes lists/name fields, and inserts `\` into the prefix table.
- `NpCreateRootDcbCcb` allocates a root directory handle context.
- `NpCreateFcb` allocates a pipe FCB:
  - Normalizes names to leading backslash.
  - Allocates full-name buffer.
  - Inserts into parent DCB list and prefix table.
  - Stores pipe instance/type/configuration metadata.
- `NpCreateCcb` allocates paged and nonpaged CCB portions:
  - Initializes inbound/outbound queues.
  - Inserts into FCB CCB list.
  - Increments current instance and server-open counts.
- `NpDeleteCcb` tears down CCB resources and queues.
- `NpDeleteFcb` cancels waiters, removes prefix/list links, releases security descriptor, and frees name/FCB memory.

## Important Interactions
- Core allocation layer for `create.c`.
- Deletion is driven by `statesup.c` and close/cleanup paths.
- Prefix table entries are consumed by `prefxsup.c`.

## Risks / Review Notes
- Event table is not usable because compare/allocate/deallocate callbacks are stubs.
- `NpDeleteCcb` decrements `CurrentInstances` but not `ServerOpenCount`; server-open accounting depends on other cleanup/close code outside this file.
- FCB deletion bugchecks if current instances remain, enforcing lifecycle ordering.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/strucsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/volinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/volinfo.c

## Purpose
Provides synthetic filesystem volume information for NPFS.

## Main Responsibilities
- `NpQueryFsVolumeInfo`:
  - Reports label `NamedPipe`.
  - `SupportsObjects = 0`.
- `NpQueryFsSizeInfo`:
  - Reports one sector per allocation unit and one byte per sector.
- `NpQueryFsDeviceInfo`:
  - Reports `FILE_DEVICE_NAMED_PIPE`.
- `NpQueryFsAttributeInfo`:
  - Reports filesystem name `NPFS`.
  - Sets `FILE_CASE_PRESERVED_NAMES`.
  - Uses max component name length `0xFFFFFFFF`.
- `NpQueryFsFullSizeInfo`:
  - Returns a zeroed full-size information structure.
- `NpCommonQueryVolumeInformation` dispatches by `FS_INFORMATION_CLASS`.
- `NpFsdQueryVolumeInformation` wraps dispatch in shared VCB locking.

## Important Interactions
- Registered as `IRP_MJ_QUERY_VOLUME_INFORMATION` in `main.c`.
- Does not inspect real pipe state; all outputs are static/synthetic.

## Risks / Review Notes
- Buffer length arithmetic is manual and unsigned.
- Size information is placeholder-like, but typical for a pseudo filesystem.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/volinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/waitsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/waitsup.c

## Purpose
Implements `FSCTL_PIPE_WAIT` waiter queue support using a wait list, cancel routines, timers, DPCs, and name matching.

## Main Responsibilities
- `NpInitializeWaitQueue` initializes list and spinlock.
- `NpAddWaiter`:
  - Allocates a wait entry.
  - Initializes timer/DPC.
  - Upcases the requested pipe name in the caller buffer.
  - Stores wait queue and wait entry in IRP driver context.
  - Installs cancel routine and queues the IRP.
  - References the file object and sets a timer.
- `NpCancelWaitQueueIrp`:
  - Removes a canceled waiter under spinlock.
  - Cancels timer if possible.
  - Dereferences file object and frees wait entry.
  - Completes the IRP with `STATUS_CANCELLED`.
- `NpTimerDispatch`:
  - Removes timed-out waiter.
  - Clears cancel routine.
  - Completes with `STATUS_IO_TIMEOUT`.
- `NpCancelWaiter`:
  - Upcases the target pipe path.
  - Scans waiters for matching names.
  - Removes matching waiters, cancels timers, and queues their IRPs on a deferred completion list with caller-supplied status.
- `NpEqualUnicodeString` compares strings without calling routines unsafe under a spinlock.

## Important Interactions
- `fsctrl.c` queues waiters in `NpWaitForNamedPipe`.
- `create.c` and `strucsup.c` cancel waiters when pipe instances appear or disappear.
- Waiter completion follows the NPFS deferred-completion pattern.

## Risks / Review Notes
- Alias-name handling in `NpCancelWaiter` contains `ASSERT(FALSE)`, and alias translation is commented out in `NpWaitForNamedPipe`; alias waits are incomplete.
- Pool tag in `NpAddWaiter` uses `NPFS_WRITE_BLOCK_TAG` instead of `NPFS_WAIT_BLOCK_TAG`.
- Timer/cancel races are carefully handled through `WaitEntry->Irp = NULL` and IRP driver context clearing.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/waitsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/write.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/write.c

## Purpose
Implements normal and fast write handling for named pipes.

## Main Responsibilities
- `NpCommonWrite`:
  - Decodes file object and validates CCB state.
  - Rejects invalid write direction based on pipe configuration.
  - Selects outbound or inbound queue based on pipe end.
  - Checks available quota and completion mode.
  - Calls `NpWriteDataQueue` to satisfy queued readers.
  - If not all data can be delivered, queues remaining data as a buffered write entry.
  - Signals event buffer when present.
- `NpFsdWrite`:
  - Uses shared VCB lock.
  - Completes IRP unless pending.
- `NpFastWrite`:
  - Calls common write without an IRP.
  - Returns false when synchronous fast I/O cannot complete.

## Important Interactions
- Write delivery is implemented in `writesup.c`.
- Pending write queue entries are managed by `datasup.c`.
- Read mode on the receiving end determines message/byte completion behavior.
- Client security context capture happens in data queue support.

## Risks / Review Notes
- Complete-operation mode for message pipes can return success with zero bytes written when quota is insufficient.
- Fast write has no IRP to pend, so quota limits can force fallback.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/write.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/writesup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/writesup.c

## Purpose
Implements delivery of write data into queued read IRPs.

## Main Responsibilities
- `NpWriteDataQueue`:
  - Iterates queued read entries while data remains.
  - Handles internal read-overflow FSCTL reads specially.
  - Copies write data into read IRP buffers or allocated intermediate buffers.
  - Captures client security context once per write and stores it on the CCB.
  - Completes read IRPs with success or `STATUS_BUFFER_OVERFLOW` depending on message/byte mode.
  - Reports remaining bytes via `BytesNotWritten`.
  - Returns `STATUS_MORE_PROCESSING_REQUIRED` when data remains and must be buffered/queued.

## Important Interactions
- Called by `write.c` and `fsctrl.c` transceive.
- Uses `NpGetNextRealDataQueueEntry` and `NpRemoveDataQueueEntry`.
- Security context capture uses `NpGetClientSecurityContext`.

## Risks / Review Notes
- Internal overflow read handling depends on FSCTL major/function fields of queued read IRPs.
- Allocated buffer ownership is transferred to IRP flags with `IRP_DEALLOCATE_BUFFER | IRP_BUFFERED_IO | IRP_INPUT_OPERATION`.
- Sparse or zero-length message behavior is represented by `MoreProcessing`, which is easy to misread.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/writesup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/CMakeLists.txt

## Purpose
Build definition for the ReactOS NTFS kernel-mode filesystem driver module.

## Main Responsibilities
- Defines the NTFS driver source list:
  - Attribute handling, block device, B-tree, cleanup/close/create, device control, directory control, dispatch, fast I/O, FCB, file info, FSCTL, MFT, misc, main NTFS code, read/write, volume info, and `ntfs.h`.
- Builds `ntfs` as a module with `ntfs.rc`.
- Sets module type to `kernelmodedriver`.
- Links against `${PSEH_LIB}`.
- Imports `ntoskrnl` and `hal`.
- Adds precompiled header `ntfs.h`.
- Installs the built driver to `reactos/system32/drivers`.

## Important Interactions
- Includes `attrib.c`, the large attribute implementation in this group.
- The PSEH dependency is required by files such as `attrib.c`, which use `_SEH2_TRY`/`_SEH2_EXCEPT`.

## Risks / Review Notes
- No conditional source selection is present; all listed files are part of the driver module.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/attrib.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/attrib.c

## Purpose
Implements NTFS attribute construction, mapping-pair/data-run conversion, cluster freeing, attribute enumeration, attribute-list reading, filename/standard-info lookup, and debug dumping for ReactOS NTFS.

## Main Responsibilities

### Attribute Constructors
- `AddBitmap` adds a resident `$BITMAP` attribute with initial 8-byte bitmap payload.
- `AddData` adds an unnamed resident empty `$DATA` attribute.
- `AddFileName` adds a `$FILE_NAME` attribute:
  - Computes parent directory by dissecting the file path and calling `NtfsFindMftRecord`.
  - Sets timestamps and archive/directory attributes.
  - Stores parent file reference and sequence information.
  - Chooses POSIX or WIN32+DOS name type based on case sensitivity and DOS 8.3 legality.
- `AddIndexAllocation` adds a named nonresident `$INDEX_ALLOCATION` attribute with empty mapping pairs.
- `AddIndexRoot` adds a resident named `$INDEX_ROOT` attribute and copies supplied index-root payload.
- `AddStandardInformation` adds `$STANDARD_INFORMATION` with current timestamps and archive attribute.

All constructor helpers only support insertion at the current `AttributeEnd` marker. They update `NextAttributeNumber` and move file-record end markers through `SetFileRecordEnd`.

### Data Run / Mapping Pair Support
- `DecodeRun` decodes NTFS mapping-pair runs into offset and length, including sparse runs as offset `-1`.
- `ConvertDataRunsToLargeMCB` converts encoded data runs to an initialized `LARGE_MCB`.
- `ConvertLargeMCBToDataRuns` converts an MCB back to encoded mapping pairs.
- `FindRun` performs a minimal first-run lookup for a nonresident attribute.
- `GetPackedByteCount` returns the minimal signed/unsigned byte count for mapping-pair encoding.
- `GetLastClusterInDataRun` walks all mapping pairs and returns the last physical cluster.

### Allocation Mutation
- `AddRun` appends allocated clusters to a nonresident attribute:
  - Adds a new MCB entry.
  - Converts MCB to mapping pairs.
  - Expands the attribute if there is room in the file record.
  - Moves trailing attributes when needed.
  - Updates `HighestVCN` and writes the file record.
  - Returns `STATUS_NOT_IMPLEMENTED` if an attribute list would be required.
- `FreeClusters` shrinks a nonresident attribute:
  - Reads the volume `$Bitmap` file.
  - Clears bits for clusters removed from the end of the MCB.
  - Writes the bitmap back.
  - Re-encodes mapping pairs.
  - Shrinks the attribute if it is the final attribute in the record.
  - Updates the file record.

### Attribute Enumeration
- `FindFirstAttribute`, `FindNextAttribute`, and `FindCloseAttribute` iterate attributes in a file record.
- `InternalReadNonResidentAttributes` loads a nonresident `$ATTRIBUTE_LIST`.
- `FindFirstAttributeListItem` and `FindNextAttributeListItem` iterate loaded attribute-list entries.
- `InternalGetNextAttribute` validates attribute lengths and stops on corrupt/out-of-range offsets.

### Lookup Helpers
- `GetFileNameFromRecord` returns a filename attribute of a requested name type, treating WIN32_AND_DOS as either WIN32 or DOS.
- `GetBestFileNameFromRecord` prefers POSIX, then WIN32, then DOS names.
- `GetStandardInformationFromRecord` finds `$STANDARD_INFORMATION`.
- `GetFileNameAttributeLength` computes variable-size filename attribute payload length.

### Debug Dumping
- `NtfsDumpFileAttributes`, `NtfsDumpAttribute`, `NtfsDumpDataRuns`, `NtfsDumpDataRunData`, and type-specific dump helpers print file-record attribute details, names, index-root contents, and mapping pairs.

## Important Interactions
- Relies heavily on NTFS structures and helpers from `ntfs.h` and other NTFS driver files:
  - `ReadFileRecord`
  - `UpdateFileRecord`
  - `FindAttribute`
  - `ReadAttribute`
  - `WriteAttribute`
  - `ReleaseAttributeContext`
  - `NtfsFindMftRecord`
  - `MoveAttributes`
  - `SetFileRecordEnd`
- Uses FsRtl large MCB APIs for run management.
- Uses volume metadata from `Vcb->NtfsInfo`, especially bytes per file record, bytes per cluster, bytes per sector, and cluster count.
- Uses the VCB file-record lookaside list for reading `$Bitmap`.

## Risks / Review Notes
- Many add-attribute paths return `STATUS_NOT_IMPLEMENTED` instead of growing into an `$ATTRIBUTE_LIST` when the file record lacks space.
- `ConvertLargeMCBToDataRuns` has a TODO for holes/sparse runs when encoding MCB entries.
- `FindRun` only decodes the first run and does not search for the run containing the requested VCN.
- `FreeClusters` returns `0` on several failure paths where an `NTSTATUS` error would be clearer.
- `FreeClusters` decrements `HighestVCN` with `min(current, current - 1)`, despite the comment saying not to go below zero; this deserves review for underflow/negative behavior.
- `AddRun` allocates a new attribute-context record without checking allocation failure before copying.
- Debug dump routines recursively print data runs and assume valid on-disk structures; they are diagnostic rather than hardened parsing paths.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/attrib.c -->