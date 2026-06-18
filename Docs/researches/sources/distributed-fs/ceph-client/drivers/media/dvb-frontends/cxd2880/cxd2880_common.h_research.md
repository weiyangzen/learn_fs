# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_common.h

## Purpose
Central common include for CXD2880 files, collecting kernel utility headers and the two's-complement conversion prototype.

## Important APIs, Types, and Functions
Includes Linux `types`, `errno`, `delay`, `bits`, and `string` headers. Declares `cxd2880_convert2s_complement()`.

## Control Flow
No control flow. It is used by most CXD2880 headers and implementation files.

## State and Persistence
No state.

## Dependencies and Integration Points
By centralizing common Linux includes, it makes low-level driver files rely on one local header for basic types, error codes, sleeps, masks, and memory helpers.

## Risks and Edge Cases
Because many files transitively depend on it, removing includes can cause broad compile failures. Adding heavy includes here increases rebuild and dependency surface.

## Test Signals
Full CXD2880 build and include-order tests for each header compiled from a clean translation unit.
