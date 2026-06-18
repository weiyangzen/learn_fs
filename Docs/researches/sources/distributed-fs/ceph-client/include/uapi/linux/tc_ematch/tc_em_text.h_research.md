# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_text.h

## Purpose
Defines the TC text ematch ABI for matching text/byte patterns with a named search algorithm over packet ranges.

## Important APIs, Types, and Constants
`TC_EM_TEXT_ALGOSIZ` is 16. `struct tcf_em_text` includes algorithm name, from/to offsets, pattern length, from/to layer bitfields, and padding.

## Control Flow, State, and Persistence
Userspace configures algorithm, layers, offsets, and pattern data. Runtime classifier searches the packet range with the selected textsearch algorithm.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC ematch and kernel textsearch implementations.

## Risks and Test Signals
Risks include unsupported algorithm names, range errors, bitfield layout, and high CPU cost on broad scans. Test known algorithms, offset boundaries, short packets, pattern length validation, and dump behavior.
