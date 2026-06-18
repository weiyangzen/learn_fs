# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_gact.h

## Purpose
Defines the generic TC action ABI for pass/drop/reclassify-style actions, including probabilistic behavior.

## Important APIs, Types, and Constants
`struct tc_gact` embeds `tc_gen`. `struct tc_gact_p` configures probability type (`PGACT_NONE`, `PGACT_NETRAND`, `PGACT_DETERM`), value, and alternate action. Attributes include timing, parameters, probability, and padding.

## Control Flow, State, and Persistence
Userspace configures a generic action and optional probability policy. Runtime action selects the configured action, possibly using random or deterministic probability logic. Counters persist in action state.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC classifier/action chains.

## Risks and Test Signals
Risks include probabilistic behavior being difficult to validate and ptype/pval interpretation mismatch. Test deterministic and random probability modes statistically, action dumps, and counter increments.
