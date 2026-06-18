# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ife.h

## Purpose
Defines the TC IFE action ABI for encoding or decoding Inter-FE metadata around packets.

## Important APIs, Types, and Constants
`IFE_ENCODE` and `IFE_DECODE` select direction. `struct tc_ife` embeds `tc_gen` and `flags`. Attributes include parameters, timing, destination/source MAC, ethertype, metadata list, and padding.

## Control Flow, State, and Persistence
Userspace configures encode or decode and optional link-layer/metadata attributes. Runtime action adds or removes IFE metadata. Action configuration and counters persist per TC action.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/pkt_cls.h>`, and `<linux/ife.h>`. Integrates with TC metadata transport between network elements.

## Risks and Test Signals
Risks include encode/decode flag confusion, metadata length mismatch, and malformed Ethernet encapsulation. Test encode/decode round trips, MAC/type settings, metadata list parsing, and packet captures.
