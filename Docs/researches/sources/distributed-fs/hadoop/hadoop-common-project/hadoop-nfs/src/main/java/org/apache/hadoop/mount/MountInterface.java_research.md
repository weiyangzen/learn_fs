# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountInterface.java

## Purpose
`MountInterface.java` defines the server-side Java contract for NFS mount protocol procedures described by RFC 1094.

## Important APIs, Types, and Functions
- `MNTPROC` enum maps mount procedure names to ordinal wire values: `NULL`, `MNT`, `DUMP`, `UMNT`, `UMNTALL`, `EXPORT`, `EXPORTALL`, and `PATHCONF`.
- `MNTPROC.getValue()` returns the ordinal.
- `MNTPROC.fromValue(int)` safely maps valid ordinals and returns null for invalid values.
- Interface methods define handlers for `nullOp`, `mnt`, `dump`, `umnt`, and `umntall`, using `XDR`, transaction id, and client `InetAddress`.
- `EXPORT`/`EXPORTALL` and `PATHCONF` handler declarations are present only as commented placeholders.

## Control Flow and State
Implementations decode request XDR where needed, write response XDR, and use client address for authorization or mount tracking. This interface itself holds no state.

## Dependencies and Integration Points
It integrates Hadoop ONCRPC `XDR` with mount daemon implementations. `MountResponse` provides helper serializers for responses to procedures defined here.

## Risks and Edge Cases
Enum ordinal order is wire-protocol significant, so reordering values would break compatibility. Invalid procedure values intentionally map to null and must be handled by dispatchers.

## Test Signals
No direct test in this subset, but protocol dispatch and response helpers rely on this enum contract.
