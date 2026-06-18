# sources/distributed-fs/ceph-client/net/llc/Makefile

## Purpose
The LLC Makefile composes the base 802.2 LLC layer and the connection-oriented LLC2 support object.

## Important APIs, Types, and Functions
`obj-$(CONFIG_LLC) += llc.o` builds core LLC from `llc_core.o`, `llc_input.o`, and `llc_output.o`. `obj-$(CONFIG_LLC2) += llc2.o` builds LLC2 from interface, event, action, connection, state-table, PDU, SAP, station, and socket files. Optional `llc_proc.o` and `sysctl_net_llc.o` are included under `CONFIG_PROC_FS` and `CONFIG_SYSCTL`.

## Control Flow
No runtime flow exists. The object lists determine which implementation pieces are linked into the LLC and LLC2 modules/objects.

## State and Persistence
No state is stored here. It affects build-time composition only.

## Dependencies and Integration Points
The Makefile ties together the state machine files (`llc_c_ev.o`, `llc_c_ac.o`, `llc_c_st.o`), PF_LLC socket API (`af_llc.o`), SAP/station support, PDU helpers, and optional observability/control files.

## Risks and Edge Cases
The LLC2 state machine relies on all listed objects; omitting one produces unresolved symbols or runtime feature gaps. Optional proc/sysctl objects must remain conditional to avoid build failures when those subsystems are disabled.

## Test Signals
Compile with LLC/LLC2 as built-in and modules, and with procfs/sysctl enabled and disabled, to catch object-list regressions.
