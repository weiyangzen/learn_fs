# sources/distributed-fs/openafs/src/butm/config

Purpose: sample tape configuration line for butm tests or manual tape module setup.

Content and format: contains `10000000 /dev/rst0`, representing a capacity and device path in the older minimal format. `test_ftm.c` documents a richer format of capacity, device name, port number, and `isafile`; this file may be a legacy example rather than directly accepted by current `test_ftm` parsing.

State and integration: no executable behavior. It points tests toward a rewind/no-rewind tape device path and therefore can drive real hardware if used unmodified.

Risks and tests: using `/dev/rst0` on a developer system can fail or touch real tape hardware. The mismatch with `test_ftm`'s four-field parser is a compatibility risk for manual testing.
