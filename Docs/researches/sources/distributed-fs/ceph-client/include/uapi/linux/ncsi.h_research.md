# sources/distributed-fs/ceph-client/include/uapi/linux/ncsi.h

## Purpose
Defines NC-SI generic netlink command and attribute ABI for inspecting packages/channels, selecting preferred interfaces, setting package/channel masks, and sending raw NC-SI commands.

## Important APIs, Types, And Functions
Exports `ncsi_nl_commands`, `ncsi_nl_attrs`, `ncsi_nl_pkg_attrs`, and `ncsi_nl_channel_attrs` with fields for ifindex, package/channel IDs, command data, masks, version, link state, active/forced flags, and VLAN lists.

## Control Flow
Userspace requests package info, sets or clears preferred package/channel combinations, sends NC-SI commands, or changes allow masks. Dump replies nest packages and channels under list attributes.

## State, Persistence, And Dependencies
State persists in NCSI device package/channel selection and masks. No external header dependencies.

## Integration Points
Used by BMC/network management tools and kernel NCSI netlink family.

## Risks
Commands require specific attribute combinations. Multi-mode and masks can alter which management channels are available, so validation and rollback matter.

## Test Signals
Validate package/channel dump nesting, preferred channel set/clear, raw command payload handling, package/channel masks, VLAN list attributes, and missing-required-attribute errors.
