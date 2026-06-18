# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_sample.h

## Purpose
Defines the TC sample action ABI for probabilistically sending packet samples to psample groups.

## Important APIs, Types, and Constants
`struct tc_sample` embeds `tc_gen`. Attributes include timing, parameters, sample rate, truncation size, psample group, and padding.

## Control Flow, State, and Persistence
Userspace sets rate/group/truncation parameters. Runtime action samples matching packets and emits sample messages while maintaining action counters.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/pkt_cls.h>`, and `<linux/if_ether.h>`. Integrates with TC and the psample generic netlink family.

## Risks and Test Signals
Risks include unexpected sampling rates, truncation larger than packet size, and missing psample listener. Test statistical sample rate, truncation, group selection, dump attributes, and counter behavior.
