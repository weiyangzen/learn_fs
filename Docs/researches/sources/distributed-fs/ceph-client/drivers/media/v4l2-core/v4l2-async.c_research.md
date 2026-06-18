# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-async.c

## Purpose
`v4l2-async.c` implements the V4L2 asynchronous subdevice registration and notifier framework. It lets bridge devices and subdevices describe expected peers by I2C address or firmware node, matches those expectations against asynchronously registered subdevices, invokes bound/unbind/complete callbacks, supports nested notifier trees, and exposes debugfs visibility for pending matches.

## Important APIs, types, and functions
Public APIs include `v4l2_async_nf_init()`, `v4l2_async_subdev_nf_init()`, `v4l2_async_nf_register()`, `v4l2_async_nf_unregister()`, `v4l2_async_nf_cleanup()`, `__v4l2_async_nf_add_fwnode()`, `__v4l2_async_nf_add_fwnode_remote()`, `__v4l2_async_nf_add_i2c()`, `v4l2_async_subdev_endpoint_add()`, `v4l2_async_connection_unique()`, `__v4l2_async_register_subdev()`, and `v4l2_async_unregister_subdev()`. Key internal lists are global `subdev_list` and `notifier_list`, plus per-notifier `waiting_list` and `done_list`, all protected by `list_lock`.

## Control flow
Notifier registration validates each match descriptor for type and global uniqueness, attempts to match all already-registered subdevices, tries nested subdevice notifiers, attempts completion from the root notifier, and finally stores the notifier in the global list. Subdevice registration initializes its async connection list, normalizes its fwnode, scans all notifiers for matches, binds repeatedly while matches exist, triggers nested notifier matching, tries completion, and if unmatched adds the subdevice to `subdev_list`. Binding registers the subdev with the root `v4l2_device` if needed, calls the notifier `bound` callback, creates ancillary media links for lens/flash entities when applicable, links the async connection to the subdev, and moves it from waiting to done.

## State and persistence behavior
All state is in-memory list topology. A notifier's `waiting_list` represents unresolved async connections; `done_list` represents bound connections. `asc->sd`, `sd->asc_list`, `notifier->parent`, and `sd->subdev_notifier` encode binding and nested notifier relationships. Fwnode match descriptors take references and release them during cleanup. Debugfs state is read-only and derived from the live lists.

## Dependencies and integration points
The file integrates V4L2 device/subdev registration, fwnode graph APIs, I2C client matching, media controller ancillary links, subdev privacy LED cleanup, debugfs, and module init/exit. Bridge drivers typically allocate notifier-specific async connection wrappers and use these APIs to wait for sensors, lenses, flashes, codecs, or other media subdevices.

## Risks and edge cases
List mutation during matching is subtle: successful binding can register new notifiers, so matching restarts from the beginning. Completion must walk the root notifier tree and ensure all child notifiers are complete. Error paths need to unbind only the connections introduced by the failing path without corrupting other notifiers. Fwnode endpoint-vs-device matching and secondary fwnodes broaden matching semantics but increase duplicate-match risk. The global mutex is critical; any callback that re-enters async APIs must avoid deadlocks.

## Test signals
Test bridge-first and subdevice-first registration order, I2C and fwnode matches, endpoint endpoint lists, duplicate match rejection, nested notifier completion, bound callback failure, complete callback failure, unregister of bound and unbound subdevices, media ancillary links for lens/flash, debugfs pending output, and fwnode reference cleanup under leak detection.
