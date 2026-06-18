# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_realm.cc

## Purpose
This file implements admin REST operations for realms and periods in the RADOS-backed RGW configuration store. It supports reading realms, listing realms, reading periods, committing periods on the master, accepting period pushes from other zones, updating local period history, and notifying the realm after successful period changes.

## Important APIs, Types, And Functions
- `RGWOp_Period_Base` centralizes period JSON response and error-stream reporting.
- `RGWOp_Period_Get` reads a period from the config store.
- `RGWOp_Period_Post` decodes a submitted period, commits new periods, accepts pushed period epochs, updates latest epoch/current period, reflects period data, and triggers realm notification.
- `RGWHandler_Period` and `RGWRESTMgr_Period` route `/admin/realm/period`.
- `RGWOp_Realm_Get` reads one realm by id or name.
- `RGWOp_Realm_List` reads the default realm id and lists known realms.
- `RGWHandler_Realm` and `RGWRESTMgr_Realm` route `/admin/realm` and register the `period` subresource.

## Control Flow
GET `/admin/realm/period` parses realm, period, and epoch arguments but ultimately reads by period id through `cfgstore->read_period()`. POST `/admin/realm/period` reads JSON into an `RGWPeriod`, rejects periods for a different realm, reloads the realm and current period from the config store, and then splits behavior. If the submitted period id is empty, it treats the request as a period commit and calls `rgw::commit_period()`, accepting `-EEXIST` as idempotent success. If the submitted period has an id, the current master zone rejects pushes whose master zone is itself. Otherwise it creates the period, updates latest epoch, attaches history if this is a new period id, may set the realm current period, or reflects a newer epoch of the current period into local objects. Responses are sent before `realm_notify_new_period()` to avoid racing connection closure.

## State And Persistence Behavior
Realm and period data persist in `s->penv.cfgstore`. POST can create period objects, update latest period epoch, update the realm's current period, reflect period data into local config objects, update in-memory period history, and send realm notifications. The `PERIOD_HISTORY_FETCH_MAX` limit prevents accepting period pushes too far ahead of local history, bounding how much intermediate history a receiver may need to fetch.

## Dependencies And Integration Points
This file depends on REST config, zone, RADOS SAL, config store, process environment, zone and mdlog services, realm writer helpers, period commit/reflect functions, and `RGWPeriodHistory`. Authorization uses `zone=read` for GET/list and `zone=write` for period POST.

## Risks And Edge Cases
`RGWOp_Period_Get` parses `realm_id` and `epoch` but reads only by `period_id` with no explicit epoch selection in this code path. POST handles idempotent retries for commit and latest-epoch updates, but period history gaps return errors. Pushed periods older than current are acknowledged without changing state; periods too far ahead return `-ENOENT`. Master-zone rejection uses `-EINVAL`, marked as a rough error code. Realm notification after response means state can be committed even if notification later fails.

## Test Signals
Tests should cover realm get/list, period get, commit with empty period id, idempotent `-EEXIST`, realm mismatch, master-zone push rejection, old period discard, too-far future rejection, missing intermediate period history, current-period update, same-period epoch reflection, and post-response notification triggering.
