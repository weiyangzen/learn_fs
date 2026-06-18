# sources/distributed-fs/ceph-client/net/openvswitch/Kconfig

## Purpose

This Kconfig file defines the kernel Open vSwitch datapath options and optional tunnel vport support. It describes OVS as an in-kernel fast path for a userspace-controlled multilayer virtual switch.

## Important APIs, Types, and Functions

The primary symbol is `OPENVSWITCH`, a tristate depending on `INET` and compatible netfilter options. It selects support libraries and protocols such as MPLS, CRC32C, MPLS GSO, destination cache, NSH, and OVS-specific conntrack/NAT modules when netfilter is enabled. Optional symbols are `OPENVSWITCH_GRE`, `OPENVSWITCH_VXLAN`, and `OPENVSWITCH_GENEVE`, each depending on `OPENVSWITCH` and its tunnel subsystem.

## Control Flow

At kernel configuration time, selecting `OPENVSWITCH` enables the main module build and selects dependencies. Tunnel options default to `OPENVSWITCH`, so they follow the main datapath unless explicitly disabled.

## State and Persistence

The file defines build-time configuration only. Runtime datapath, vport, flow, and conntrack state are implemented in C files.

## Dependencies and Integration Points

The dependency expression ensures OVS is built only with compatible netfilter conntrack, NAT, defrag, and conncount availability. The selects wire OVS to NSH, MPLS, conntrack, NAT, and tunnel modules used by actions and vports.

## Risks and Edge Cases

The netfilter dependency expression is subtle: configurations with partial conntrack/NAT support can alter available OVS action behavior. Because tunnel options default on, binary size and exposed vport types may be larger than expected unless disabled.

## Test Signals

Configuration tests should validate OVS with and without NF_CONNTRACK/NF_NAT/NETFILTER_CONNCOUNT, and ensure tunnel symbols produce the corresponding `vport-*.o` objects. Build tests should cover built-in and module combinations.
