## sources/cloud-native/containers-storage/pkg/idtools/usergroupadd_linux.go

Purpose: Linux helper to create a system user/group and subordinate UID/GID ranges for namespace remapping.

Important APIs/types/functions: `AddNamespaceRangesUser`, `addUser`, `createSubordinateRanges`, `findNextUIDRange`, `findNextGIDRange`, `findNextRangeStart`, and `wouldOverlap`.

Control flow: chooses `adduser` or `useradd` once, creates the user, runs `id` and parses UID/GID, checks whether subuid/subgid ranges already exist, finds the next non-overlapping range starting at 100000, and uses `usermod -v/-w` to add ranges.

State and persistence: mutates host user/group databases and subordinate ID files through system commands; caches selected user creation command.

Dependencies and integration points: supports automatic namespace user setup. Depends on external commands, delayed regexp, and subordinate range readers.

Risks: highly host-distribution dependent and requires privileges. `wouldOverlap` treats range endpoints inclusively and may be conservative/off by one around adjacent ranges. No locking around subuid/subgid allocation, so concurrent invocations can race.

Test signals: no selected tests directly exercise user creation or range allocation.
