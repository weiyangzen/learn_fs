<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/regulator/regulator.h -->
# sources/distributed-fs/ceph-client/include/uapi/regulator/regulator.h

## Purpose
Defines the userspace generic-netlink ABI for regulator event notifications, including event bit masks, event payload structure, family name/version, multicast group, and command/attribute IDs.

## Important APIs, Types, and Functions
Read coverage: 86 lines and 2878 bytes. Visible type families include struct reg_genl_event. Important macros/constants include _UAPI_REGULATOR_H, REGULATOR_EVENT_UNDER_VOLTAGE, REGULATOR_EVENT_OVER_CURRENT, REGULATOR_EVENT_REGULATION_OUT, REGULATOR_EVENT_FAIL, REGULATOR_EVENT_OVER_TEMP, REGULATOR_EVENT_FORCE_DISABLE, REGULATOR_EVENT_VOLTAGE_CHANGE, REGULATOR_EVENT_DISABLE, REGULATOR_EVENT_PRE_VOLTAGE_CHANGE, REGULATOR_EVENT_ABORT_VOLTAGE_CHANGE, REGULATOR_EVENT_PRE_DISABLE, REGULATOR_EVENT_ABORT_DISABLE, REGULATOR_EVENT_ENABLE, REGULATOR_EVENT_UNDER_VOLTAGE_WARN, REGULATOR_EVENT_OVER_CURRENT_WARN, REGULATOR_EVENT_OVER_VOLTAGE_WARN, REGULATOR_EVENT_OVER_TEMP_WARN, REGULATOR_EVENT_WARN_MASK, REG_GENL_ATTR_MAX, REG_GENL_CMD_MAX, REG_GENL_FAMILY_NAME, REG_GENL_VERSION, REG_GENL_MCAST_GROUP_NAME. Explicit ioctl-style command names include none.

## Control Flow
Kernel regulator core publishes generic-netlink multicast messages on `reg_event`/`reg_mc_group` when voltage/current/temperature/enable/disable events occur. Userspace subscribes, receives `reg_genl_event`, and interprets the bitmask plus regulator name attribute.

## State and Persistence Behavior
The header stores no state. Runtime state is in regulator devices and the generic-netlink multicast notification path; events represent transient condition changes and warnings.

## Dependencies and Integration Points
It depends on Linux integer types and generic-netlink conventions. It integrates with regulator core notifiers, power-management daemons, monitoring tools, and device-specific regulator drivers. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Event bit stability and family/group names are userspace ABI. Warning-mask composition must include only warn bits, and regulator names must be bounded and consistently encoded in netlink attributes.

## Test Signals
Trigger each regulator notifier event in test drivers or fault-injection setups, verify generic-netlink family discovery, multicast subscription, event bit decoding, name attribute presence, and compatibility with older userspace listeners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/regulator/regulator.h -->
