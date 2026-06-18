# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode_i.h

## Purpose
`testmode_i.h` holds the internal nl80211 testmode attribute IDs and command number used by WCN36xx production-test handling.

## Important APIs, Types, and Functions
- `WCN36XX_TM_DATA_MAX_LEN` caps binary test payloads at 5000 bytes.
- `enum wcn36xx_tm_attr` defines command and data attributes with the standard max marker.
- `WCN36XX_TM_CMD_PTT` is the accepted testmode command selector.

## Control Flow
There is no runtime control flow. `testmode.c` uses these constants to build the netlink policy and to reject unsupported commands.

## State and Persistence Behavior
The file defines ABI constants only. The values persist as part of the userspace-visible testmode protocol.

## Dependencies and Integration Points
It is included by `testmode.c` and indirectly tied to nl80211 netlink parsing. It intentionally stays small and private to avoid exposing internal attribute names beyond the driver implementation.

## Risks and Test Signals
Changing numeric values would break userspace tooling. Test signals are netlink policy validation, command rejection for unknown IDs, and fuzzing of oversized binary payloads.
