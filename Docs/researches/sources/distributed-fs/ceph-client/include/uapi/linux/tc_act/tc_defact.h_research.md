# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_defact.h

## Purpose
Defines the generic/default TC action ABI used to carry opaque action data with standard `tc_gen` parameters.

## Important APIs, Types, and Constants
`struct tc_defact` embeds `tc_gen`. Attributes are `TCA_DEF_TM`, `TCA_DEF_PARMS`, `TCA_DEF_DATA`, and `TCA_DEF_PAD`.

## Control Flow, State, and Persistence
Userspace configures generic action parameters and optional data. Kernel action implementation interprets the data; generic counters and timing state persist per action instance.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC action core and `tc` netlink messages.

## Risks and Test Signals
Risks include opaque data versioning and mismatched userspace/kernel interpretation. Test action creation, dump round trip, unknown data rejection, and generic action counter updates.
