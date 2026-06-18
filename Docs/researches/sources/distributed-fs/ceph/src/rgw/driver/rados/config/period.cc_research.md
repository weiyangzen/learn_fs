# sources/distributed-fs/ceph/src/rgw/driver/rados/config/period.cc

Purpose: Implements period object storage for multisite configuration, including epoch-specific period objects, latest-epoch tracking, deletion, and listing of period ids.

Important APIs/types/functions: `period_oid()` maps period id/epoch to `periods.<id>.<epoch>`, except staging ids ending `:staging` omit epoch. `latest_epoch_oid()` builds the latest-epoch object name. `update_latest_epoch()` atomically advances the latest epoch with retries. `create_period()`, `read_period()`, `delete_period()`, and `list_period_ids()` implement the SAL config-store period API.

Control flow: `read_period()` reads latest epoch first when no epoch is supplied, then reads the period object. `update_latest_epoch()` loops up to 20 times, reading current latest, rejecting non-increasing epochs with `-EEXIST`, using exclusive create for initial write, and retrying on `-EEXIST` or version conflict. `delete_period()` reads latest epoch, removes epochs from 0 through latest, then removes the latest-epoch object.

State/persistence: Period data lives in `impl->period_pool`. Latest epoch state is encoded `RGWPeriodLatestEpochInfo`; period objects are encoded `RGWPeriod`. Listing period ids scans latest-epoch objects, not period data objects, so a period without latest-epoch metadata is invisible to list.

Dependencies/integration: Uses `RadosConfigStore`, `ConfigImpl`, RGW period types, `RGWObjVersionTracker`, and configurable latest-epoch suffix from Ceph config.

Risks: Deletion assumes epoch range is dense from 0 to latest and treats missing objects as ignorable. Staging period oid behavior differs from normal periods and must not collide with epoch objects. Concurrent latest-epoch updates can fail after retry exhaustion with `-ECANCELED`.

Test signals: Exercise initial latest-epoch create races, non-increasing update rejection, reading explicit vs latest epoch, staging oid behavior, deletion with missing epoch objects, and listing only latest-epoch-backed ids.
