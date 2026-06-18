# sources/distributed-fs/ceph/src/rgw/rgw_period_pusher.cc

## Purpose
`rgw_period_pusher.cc` implements background propagation of realm period updates from zone masters to peer zones and zonegroups. It responds to realm notifications, decides which peers need a period, and posts the period over REST with retry/backoff.

## Important APIs, Types, And Functions
`PushAndRetryCR` posts one period to one `RGWRESTConn` with exponential backoff. `PushAllCR` spawns a push coroutine per connection and drains them. `RGWPeriodPusher::CRThread` runs the coroutine manager and HTTP manager in a background thread. `RGWPeriodPusher` handles notifications, pause/resume during realm reload, and startup push of current period.

## Control Flow
Construction reads the current period and immediately processes it. `handle_notify()` decodes a `RGWPeriod`, queues notifications while paused, rejects stale period/realm epochs, verifies this zone's zonegroup, exits if this zone is not the master, builds connections to peer zonegroups if it is also the master zonegroup, builds connections to peer zones in its zonegroup, updates epoch tracking, and replaces the active coroutine thread. Each push retries every endpoint before sleeping, with exponential backoff bounded by config.

## State And Persistence
The pusher does not persist data locally; it transmits already-persisted period objects to peers. State includes current realm/period epoch sent, pending notifications while paused, a driver pointer that can be nulled during reconfiguration, and the active coroutine thread.

## Dependencies And Integration Points
It depends on realm watcher/reloader interfaces, SAL driver/zone config, `RGWRESTConn`, `RGWPostRESTResourceCR`, coroutine manager, HTTP manager, period JSON encoding, and config options `rgw_period_push_interval*`. It complements `RGWPeriodPuller`: peers may receive pushes or later pull missing periods.

## Risks And Test Signals
Risks include infinite retry on permanently unreachable peers, replacing active threads while pushes are in flight, driver access during reload, stale notification suppression, and incomplete peer selection. Tests should cover stale/newer notifications, master versus non-master zones, peer zonegroup and zone connection construction, pause/resume queue drain, retry/backoff behavior, and thread cleanup.
