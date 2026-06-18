# sources/distributed-fs/ceph-client/net/nsh/Kconfig

## Purpose

This Kconfig file defines the `NET_NSH` build option for Linux Network Service Header support. It documents that the implementation targets Service Function Chaining per RFC 7665 and currently supports MD type 1 only, primarily for Open vSwitch integration.

## Important APIs, Types, and Functions

There are no C APIs in this file. The important symbol is `NET_NSH`, a tristate menuconfig option titled "Network Service Header (NSH) protocol" with default `n`.

## Control Flow

At configuration time, enabling `NET_NSH` causes `net/nsh/Makefile` to build `nsh.o`. Open vSwitch selects this symbol when OVS is enabled, making NSH push/pop helpers available to OVS actions.

## State and Persistence

The only persistent state is the kernel build configuration choice. No runtime state is defined here.

## Dependencies and Integration Points

The help text identifies Open vSwitch as the current consumer. `net/openvswitch/Kconfig` selects `NET_NSH`, and `nsh.c` exports helper symbols used by OVS action execution.

## Risks and Edge Cases

The help text narrows support to MD type 1 and Open vSwitch. Users expecting generic NSH handling or other metadata types may overestimate the feature.

## Test Signals

Configuration tests should verify that selecting Open vSwitch selects `NET_NSH`, that `NET_NSH=m/y` builds `nsh.o`, and that disabling it removes NSH protocol object compilation unless selected by a dependent feature.
