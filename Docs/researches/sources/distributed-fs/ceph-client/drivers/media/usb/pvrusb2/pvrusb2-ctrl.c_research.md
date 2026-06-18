<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.c

Purpose: generic pvrusb2 control abstraction used by V4L2, sysfs, and internal code to get/set hardware controls and convert values to/from symbolic strings.

Important APIs/types/functions: `pvr2_ctrl_set_value()`, `pvr2_ctrl_set_mask_value()`, `pvr2_ctrl_get_value()`, min/max/default/count/mask/name/description accessors, V4L ID/flag helpers, custom symbol hooks, `pvr2_ctrl_sym_to_value()`, and `pvr2_ctrl_value_to_sym()`. Internal parsers handle integers, booleans, enums, and bitmask token lists. All hardware access is serialized with `hdw->big_lock`.

Control flow: setters validate type/range, mask bitmask controls, and invoke the control descriptor's `set_value` callback. Getters lock and delegate to descriptor callbacks or defaults. Symbol parsing trims whitespace, parses enum/bool names or numeric tokens, and produces mask/value pairs. Symbol formatting emits numeric, bool, enum names, or bitmask names.

State and persistence: no independent state. It operates on `struct pvr2_ctrl` and its descriptor stored in the hardware layer. Setting a control may mark dirty state or program hardware depending on the callback.

Dependencies and integration: includes pvrusb2 hardware internals for lock macros and control descriptor types; used by V4L2 ioctl glue and sysfs/debug interfaces.

Risks: lock macros rely on `hdw->big_lock` and held-state fields; callbacks must not recurse incorrectly. Bitmask string generation has a suspicious branch that prints `+0x...` for bits in `um & ~val` where a minus marker might be expected. Some helpers return neutral values for NULL controls, which can hide caller bugs. Symbol parsing accepts numeric fallbacks, so invalid names that parse as numbers can pass range checks.

Test signals: sysfs/V4L2 get/set for int, bool, enum, and bitmask controls; range-boundary tests; custom symbol conversions; lockdep under concurrent control access; invalid-token tests returning `-EINVAL` or `-ERANGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.c -->
