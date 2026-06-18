# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-statedump.h

## Purpose
`glusterd-statedump.h` is the public declaration point for glusterd's private statedump hook.

## Important APIs, Types, and Functions
It includes `glusterfs/xlator.h` and declares `int glusterd_dump_priv(xlator_t *this);`. No types are defined locally.

## Control Flow
There is no runtime control flow. The header allows glusterd's xlator setup code to register the implementation in `glusterd-statedump.c`.

## State and Persistence Behavior
The header has no state or persistence behavior. It exposes an API that reads in-memory glusterd state during a statedump.

## Dependencies and Integration Points
The only dependency is the `xlator_t` declaration. Integration is with glusterd's xlator callback table and the GlusterFS statedump subsystem.

## Risks and Edge Cases
The header does not document ownership or locking expectations. Callers must rely on the implementation to handle locking and tolerate a missing `this->private`.

## Test Signals
Build coverage is the primary signal: code that includes this header should compile and link against `glusterd_dump_priv()`. Runtime behavior is tested through `glusterd-statedump.c`.
