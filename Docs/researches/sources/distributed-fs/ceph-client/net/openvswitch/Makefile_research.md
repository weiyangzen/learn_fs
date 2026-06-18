# sources/distributed-fs/ceph-client/net/openvswitch/Makefile

## Purpose

This Makefile defines the Open vSwitch module composition and optional vport objects.

## Important APIs, Types, and Functions

The main object is `openvswitch.o`, built from action execution, datapath control, notification, flow parsing/table, meter, tracing, and vport source files. `conntrack.o` is added when `CONFIG_NF_CONNTRACK` is set. Optional tunnel modules are `vport-vxlan.o`, `vport-geneve.o`, and `vport-gre.o`. The trace object gets `-I$(src)`.

## Control Flow

Kbuild combines `openvswitch-y` into `openvswitch.o` for `CONFIG_OPENVSWITCH`. Optional object lines attach tunnel implementations to their own configuration symbols.

## State and Persistence

No runtime state is represented here. The file determines which code is present in the compiled kernel/module.

## Dependencies and Integration Points

It mirrors Kconfig feature gates and ensures datapath code is linked with flow, meter, vport, and tracing subsystems. Conditional conntrack inclusion matches the stubs in `conntrack.h`.

## Risks and Edge Cases

Feature mismatches can happen if callers assume conntrack or tunnel actions exist when their object was not built. Trace include flags are local to `openvswitch_trace.o`.

## Test Signals

Build tests should verify `openvswitch.o` composition with conntrack enabled/disabled and each tunnel option as built-in/module/off. Symbol tests should ensure `ovs_ct_*` references resolve to real code or stubs according to configuration.
