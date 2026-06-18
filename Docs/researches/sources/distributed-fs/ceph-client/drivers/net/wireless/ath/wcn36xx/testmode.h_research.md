# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode.h

## Purpose
`testmode.h` defines the public WCN36xx nl80211 testmode payload structures and provides the `wcn36xx_tm_cmd()` declaration or stub depending on `CONFIG_NL80211_TESTMODE`.

## Important APIs, Types, and Functions
- `struct ftm_rsp_msg` is the packed firmware test message wrapper containing message ID, body length, response status, and flexible response bytes.
- `struct ftm_payload` wraps an FTM command type with an embedded `ftm_rsp_msg`.
- `MSG_GET_BUILD_RELEASE_NUMBER` identifies the locally handled version query.
- `wcn36xx_tm_cmd()` is exported when testmode is enabled; otherwise an inline stub returns success so callers can compile without conditional code.

## Control Flow
The header has no active control flow. Its conditional compilation path determines whether cfg80211 testmode calls are wired to `testmode.c` or become a no-op.

## State and Persistence Behavior
The structures describe transient netlink/firmware payloads. They do not own persistent state, but their packed layout is part of the userspace-driver-firmware test ABI.

## Dependencies and Integration Points
The header includes `wcn36xx.h` for mac80211 types and driver context. It is consumed by the WCN36xx mac80211 operations and by `testmode.c`.

## Risks and Test Signals
The main risk is ABI mismatch in packed binary layouts or the disabled-testmode stub hiding unsupported userspace expectations. Test signals are allmodconfig build coverage, nl80211 testmode attribute interoperability, and correct version query layout.
