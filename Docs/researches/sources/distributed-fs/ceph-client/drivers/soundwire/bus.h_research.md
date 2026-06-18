# sources/distributed-fs/ceph-client/drivers/soundwire/bus.h

## Purpose
Defines private SoundWire core declarations shared across bus, discovery, debugfs, IRQ, stream, and master-library code. It supplies message structures, BPT structures, stream runtime structures, helper prototypes, and small inline fillers for transport and port parameters.

## Important APIs, Types, and Functions
Important types are `struct sdw_msg`, `struct sdw_bpt_section`, `struct sdw_bpt_msg`, `struct sdw_port_runtime`, `struct sdw_slave_runtime`, `struct sdw_master_runtime`, and `struct sdw_transport_data`. It declares discovery and device APIs (`sdw_acpi_find_slaves()`, `sdw_of_find_slaves()`, `sdw_slave_add()`, `sdw_master_device_add()`), debugfs APIs with stubs, transfer APIs, DPN interrupt configuration, broadcast test helpers, status clearing, modalias generation, and `sdw_compute_slave_ports()`. Inline helpers `sdw_fill_xport_params()` and `sdw_fill_port_params()` populate stream programming structures.

## Control Flow
The header does not execute independently. Its stubs make non-ACPI and non-debugfs builds compile by returning `-ENOTSUPP` or doing nothing. Runtime code uses `sdw_msg` to pass fully prepared register commands to master drivers, `sdw_bpt_msg` for bulk transport, and the runtime list structures to compute and apply stream parameters.

## State and Persistence Behavior
The declared runtime structures are embedded in `struct sdw_stream_runtime` and bus/slave lists. Their state persists for the lifetime of stream configuration and records port numbers, channel masks, transport/port parameters, lanes, directions, and list membership. `sdw_msg` and `sdw_bpt_msg` are transient command descriptors.

## Dependencies and Integration Points
This header is the local bridge between generic SoundWire core code, master drivers such as AMD/Cadence/Intel/Qualcomm, debugfs, IRQ-domain support, and stream/bandwidth allocation. It assumes public SoundWire types and constants from `<linux/soundwire/sdw.h>` are already visible through includers.

## Risks
Changing structure fields or helper semantics affects multiple modules in one directory. The `sdw_msg.addr` field is 16-bit while APIs accept larger addresses with paging, so callers must use `sdw_fill_msg()`. Debugfs and ACPI stubs must remain signature-compatible with enabled implementations. Runtime list nodes require strict ownership to avoid list corruption during stream add/remove.

## Test Signals
Compile matrix coverage with ACPI enabled/disabled, debugfs enabled/disabled, and IRQ-domain enabled/disabled is essential. Runtime signals include stream add/remove list integrity, correct transport/port parameters passed into master port ops, paged message transfers, BPT message submission, and slave status clearing after master reset.
