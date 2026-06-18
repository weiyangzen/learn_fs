# sources/distributed-fs/lizardfs/src/master/matotsserv.h

## Purpose

`matotsserv.h` declares the public interface for LizardFS master tapeserver integration. It exposes service initialization, file enqueue capability, file enqueueing, and tapeserver status lookup/listing. The file was read as a complete 45-line header.

## Important APIs, Types, and Functions

It defines `TapeserverId` as `uint32_t` and declares `matotsserv_init`, `matotsserv_can_enqueue_node`, `matotsserv_enqueue_node`, `matotsserv_get_tapeserver_info`, and `matotsserv_get_tapeservers`. Public parameter/return types include `TapeKey` and `TapeserverListEntry`.

## Control Flow

No executable flow exists in the header; callers use it to decide whether tape copy work can be queued and to retrieve connected tapeserver metadata.

## State and Persistence Behavior

The header owns no state. Returned IDs refer to runtime tapeserver registrations and filesystem tape-copy associations maintained elsewhere.

## Dependencies and Integration Points

It includes ID pool, tape key/copy info, and network address definitions. It integrates filesystem operations that enqueue archival copies and admin/status handlers that display tapeserver state.

## Risks and Edge Cases

Callers must respect `matotsserv_can_enqueue_node` before enqueueing. `TapeserverId` identity is implementation-defined by the service and should not be assumed globally stable without checking the implementation.

## Test Signals

Compile coverage from filesystem goal/tape paths and integration tests that connect a tapeserver, enqueue a file, and retrieve its status.
