# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/MasterBlockLocation.java

## Purpose
`MasterBlockLocation` is an immutable value object representing a block replica location by worker ID and storage tier alias.

## Important APIs and Types
- Fields: `mWorkerId`, `mTierAlias`.
- Package-private constructor.
- Public getters `getWorkerId` and `getTierAlias`.
- Value semantics via `equals`, `hashCode`, and `toString`.

## Control Flow
There is no complex control flow. Instances are created with worker/tier values and can be compared or used as map/set keys.

## State and Persistence Behavior
The object is immutable and thread-safe. It performs no journaling or persistence itself. In this source tree, newer block-location paths use proto `BlockLocation` and `BlockLocationUtils`; this class is a metadata value representation where used by stores or older code.

## Dependencies and Integration Points
It depends on Guava `MoreObjects` and `Objects`. It belongs to the block metadata package and represents a simplified location without medium type.

## Risks and Edge Cases
Equality includes only worker ID and tier alias. If a caller needs medium type or additional location attributes, this value object is insufficient. Constructor package visibility limits external misuse.

## Test Signals
No direct test was found in the immediate search. Behavior is simple value-object behavior likely covered indirectly by metadata store tests when this type is used.
