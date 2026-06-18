<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/policy/Policy.cc -->
# sources/distributed-fs/eos/mgm/policy/Policy.cc

Source read size: 846 lines, 30722 bytes.

## Purpose

Implements EOS MGM policy resolution for layout, space, forced placement, local redirect, conversion, read/write QoS fields, and proc policy command stubs.

## Important APIs, Types, and Functions

Key functions are `GetDefaultSizeFactor`, `GetSpacePolicyLayout`, `GetLayoutAndSpace`, `GetPlctPolicy`, `RedirectLocal`, `HasUpdConversion`, `HasReadConversion`, `UpdateConversion`, `ReadConversion`, `Set`, `Ls`, `Rm`, `Get`, `IsProcConversion`, `GetRWValue`, `GetRWConfigKeys`, and `RWParams::getKeys`. Static key lists define base policy and read/write policy names.

## Control Flow

`GetLayoutAndSpace` starts from explicit env layout/checksum/stripe/block settings, loads default and selected-space policies from `FsView`, applies read/write policy overrides by app/user/group/default priority, injects nonempty space policies into missing `sys.forced.*` attributes, processes explicit/forced space and group choices, optionally moves writes to the first under-nominal alternative space, applies sys forced layout/checksum/block/stripe/QoS/schedule settings, then applies user forced settings unless disabled. It outputs the final layout id, space, forced fs/group, bandwidth, schedule, I/O priority/type, atime age, and alternate checksums. `GetPlctPolicy` resolves scattered/hybrid/gathered placement and target geotag. Conversion helpers parse `space:layout` targets and return async/none/fail. Redirect logic returns never/always/optional based on xattrs, env override, and layout type.

## State and Persistence Behavior

The functions are mostly read-only, but `GetLayoutAndSpace` mutates the provided attribute map by injecting policy-derived `sys.forced.*` entries. Policy values are read from `FsView` space configuration; no persistent writes are implemented here (`Set` is effectively a stub).

## Dependencies and Integration Points

Integrates `LayoutId`, `FsView`, quota/nominal-space checks, namespace xattrs, `VirtualIdentity`, XRootD env parsing, conversion proc paths, alt checksum policy, and scheduler placement policy enums.

## Risks and Edge Cases

The policy precedence chain is complex: env, default space config, selected/alternative space config, sys forced xattrs, and user forced xattrs interact. Alternative-space selection only runs on writes. `std::stoi` for conversion layout can throw if malformed. `Set`, `Ls`, and `Get` are stubs/empty, so proc policy management may not do what callers expect. Logging format for layout id appears to pass layout/layoutId in reversed order.

## Test Signals

Use table-driven tests for policy precedence, noforce flags, root overrides, default/nondefault/alternative space policies, forced group/fsid, checksum noforce, alt checksum computation, read/write QoS keys by app/user/group, local redirect modes, placement policy geotag sanitation, conversion parsing and quota suppression, and malformed policy values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/policy/Policy.cc -->
