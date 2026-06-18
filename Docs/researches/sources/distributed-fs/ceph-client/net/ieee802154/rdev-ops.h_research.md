## sources/distributed-fs/ceph-client/net/ieee802154/rdev-ops.h

Purpose: inline dispatch layer from cfg802154/nl802154 code to driver `cfg802154_ops`. It wraps most operations with tracepoints and optional-operation checks, keeping call sites concise and consistent.

Important APIs/types/functions: wrappers include deprecated and modern virtual interface add/delete, suspend/resume, channel/CCA/ED/tx-power setters, PAN ID/short-address setters, CSMA/backoff/frame-retry/LBT/ackreq setters, scan trigger/abort, beacon start/stop, associate/disassociate, and experimental LLSEC table/parameter/key/device/security-level operations. Most non-LLSEC wrappers call `trace_802154_rdev_*` before the driver op and `trace_802154_rdev_return_int()` after return.

Control flow and state: wrappers do not own persistent state; they pass `&rdev->wpan_phy` and sometimes `wpan_dev` or request structures to driver callbacks. Optional operations return `-EOPNOTSUPP` when absent for scan, beacon, association, and disassociation; many basic setters assume the operation exists because command exposure/driver registration should guarantee it.

Dependencies and integration points: depends on `net/cfg802154.h`, private `core.h`, and `trace.h`. Heavily used by `nl802154.c`, legacy `nl-phy.c`, and potentially power-management paths.

Risks: wrappers that do not check for NULL ops rely on higher-level supported-command gating and driver correctness; a missing callback can crash. Request ownership for scan/beacon wrappers is delegated to driver on success and caller on failure. Experimental LLSEC wrappers are untraced and assume ops exist under config.

Test signals: tracepoint presence around successful and failing ops, unsupported optional operations returning `-EOPNOTSUPP`, command exposure matching non-NULL callbacks, driver callback argument correctness, and LLSEC behavior under `CONFIG_IEEE802154_NL802154_EXPERIMENTAL`.
