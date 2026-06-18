<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_forward.h -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_forward.h

## Purpose
Declares the HSR/PRP forwarding and frame-conversion interface used by the device protocol ops.

## APIs, Types, and Functions
Declares `hsr_forward_skb()`, PRP/HSR tagged frame creation, untagged frame extraction, protocol-specific drop decisions, and protocol-specific frame-info fill functions.

## Control Flow, State, and Persistence
No runtime logic is present. The header forms the contract between `hsr_device.c` protocol operation tables and `hsr_forward.c` implementations.

## Dependencies and Integration
Depends on `linux/netdevice.h`, `hsr_main.h`, and `struct hsr_frame_info` from `hsr_framereg.h`. Consumers are mainly `hsr_device.c` and implementation-local peers.

## Risks and Test Signals
Risks include signature drift between protocol ops and declarations or incorrect assumptions about skb ownership. Test signals are successful build and exercise of HSR and PRP protocol ops through `hsr_forward_skb()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_forward.h -->
