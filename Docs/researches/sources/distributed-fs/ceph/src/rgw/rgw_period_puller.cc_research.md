# sources/distributed-fs/ceph/src/rgw/rgw_period_puller.cc

## Purpose
`rgw_period_puller.cc` implements `RGWPeriodPuller`, the `RGWPeriodHistory::Puller` used to obtain missing periods locally or from the multisite master zone.

## Important APIs, Types, And Functions
`RGWPeriodPuller::pull()` is the public implementation. Internal `pull_period()` builds a synthetic admin REST GET for `/admin/realm/period`, forwards it through an `RGWRESTConn`, parses the JSON response, and decodes an `RGWPeriod`.

## Control Flow
`pull()` first tries `cfgstore->read_period()`. If local read fails and this zone is metadata master, it returns the failure. Otherwise it forwards a request to the master connection, rewrites the pulled period to a new local id and first epoch, creates it locally with exclusive create, updates latest epoch, optionally reflects it if it is the realm's current period, and tolerates `-EEXIST` for already-stored periods or latest epochs.

## State And Persistence
The function writes pulled periods into the local config store and updates latest-epoch metadata. It can also call `rgw::reflect_period()` to update local reflected realm/zone config for the latest current period.

## Dependencies And Integration Points
It depends on zone services, sysobj service references, `RGWRESTConn`, admin REST forwarding, HTTP error translation, JSON parsing, and config-store period APIs. `RGWPeriodHistory::attach()` calls it when predecessor periods are missing.

## Risks And Test Signals
Risks include master-zone unavailability, response size cap (`128 KiB`), malformed JSON, id/epoch rewriting assumptions, races with concurrent period creation, and reflection failure after storage succeeds. Tests should cover local hit, local miss on master zone, remote pull success, remote HTTP/JSON/decode failures, duplicate create/latest epoch, and current-period reflection.
