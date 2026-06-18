# sources/distributed-fs/ceph-client/drivers/net/vxlan/Makefile

## Purpose
This Makefile builds the Linux VXLAN driver as a composite `vxlan.o` object when `CONFIG_VXLAN` is enabled.

## Important APIs, Types, And Functions
`obj-$(CONFIG_VXLAN) += vxlan.o` connects the directory to Kbuild configuration. `vxlan-objs := vxlan_core.o vxlan_multicast.o vxlan_vnifilter.o vxlan_mdb.o` declares the component objects linked into the final driver object.

## Control Flow
There is no runtime control flow. Kbuild evaluates `CONFIG_VXLAN`; if enabled, it compiles the listed object files and links them into `vxlan.o`.

## State And Persistence
No runtime state. Build state is the dependency relationship among `CONFIG_VXLAN`, `vxlan.o`, and component objects.

## Dependencies And Integration Points
Integrates with kernel Kbuild and VXLAN source files in the same directory. Source additions/removals must be reflected here.

## Risks
Missing objects can omit functionality or cause unresolved symbols; stale objects break compilation. Both built-in and module configurations need coverage.

## Test Signals
Build with `CONFIG_VXLAN` disabled, built-in, and as a module; verify all four component objects participate in `vxlan.o`.
