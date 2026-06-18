# sources/distributed-fs/ceph-client/include/linux/fpga/fpga-bridge.h

## Purpose
This header defines FPGA bridge devices, operations, registration, lookup, and list helpers. Bridges gate traffic between the processor system and FPGA fabric during reconfiguration.

## APIs, types, and control flow
`struct fpga_bridge_ops` provides status, enable/disable, remove-state, and optional sysfs groups. `struct fpga_bridge_info` is the stable registration input. `struct fpga_bridge` embeds a device, mutex, ops owner, image info pointer, list node, and private data. Consumers get bridges by device or OF node, enable/disable individual bridges, aggregate them into lists, enable/disable/put lists, and register/unregister providers through module-owner-wrapped macros.

## State and dependencies
Bridge state includes exclusive-reference mutex, module ownership, associated `fpga_image_info`, and low-level private data. It depends on the FPGA manager image-info type, device tree, lists, modules, and device core lifetime.

## Integration, risks, and tests
FPGA regions coordinate bridges with manager loads: disable bridges, program fabric, then re-enable. Risks are unbalanced get/put, enabling traffic before programming completes, module removal while ops are active, and partial list failure rollback. Tests should cover individual enable/disable, bridge list rollback on failure, OF lookup, unregister with active refs, sysfs attribute exposure, and timeout handling from image info.
