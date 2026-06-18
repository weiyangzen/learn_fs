# sources/distributed-fs/lizardfs/src/master/matocsserv.h

## Purpose

`matocsserv.h` is the public master-facing interface for the chunkserver service implemented in `matocsserv.cc`. It forward-declares opaque connection and chunkserver DB types and exposes functions used by chunk placement, chunk operation scheduling, status reporting, and module initialization. The source was read as a complete 127-line header.

## Important APIs, Types, and Functions

The header defines `matocsserventry`, `csdbentry`, `Chunkservers`, `ServerWithUsage`, and `IpCounter`. APIs cover label/usage/version/location accessors, sorted/filtered server selection, new-chunk placement for a goal, total/available space aggregation, replication/deletion counters, operation senders for create/delete/replicate/set-version/duplicate/truncate/duptrunc, initialization, and conversion to `ChunkserverListEntry`.

## Control Flow

The header has no executable control flow. It defines the call surface used by other master modules to ask the chunkserver service for placement candidates and to enqueue protocol messages to active chunkservers.

## State and Persistence Behavior

It owns no state directly. Exposed pointer types refer to connection records maintained by `matocsserv.cc`; callers must treat them as live runtime handles, not durable identities.

## Dependencies and Integration Points

It includes chunk part types, goal/media-label definitions, server selection helpers, `ChunkserverListEntry`, and compact map/vector utilities. It is integrated with the chunks module, admin/status paths, and placement algorithms that need chunkserver handles.

## Risks and Edge Cases

Opaque `matocsserventry*` handles can become invalid after disconnect cleanup, so users must not persist them beyond the chunkserver service lifecycle. The API exposes multiple version-sensitive operation senders; callers must pass compatible `ChunkPartType` values and source vectors.

## Test Signals

Compile/link coverage for all users, placement unit tests that mock connected servers, and integration tests that enqueue every declared chunk operation through live or simulated chunkserver entries.
