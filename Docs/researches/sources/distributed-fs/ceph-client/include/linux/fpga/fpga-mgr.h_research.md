# sources/distributed-fs/ceph-client/include/linux/fpga/fpga-mgr.h

## Purpose
This header defines the FPGA manager framework interface. Managers own the programming sequence and state machine for loading bitstreams into FPGA hardware.

## APIs, types, and control flow
`enum fpga_mgr_states` describes power, request, parse, write, complete, error, and operating states. Image flags select partial/external/encrypted/LSB-first/compressed bitstreams. `struct fpga_image_info` carries firmware name, scatterlist or buffer, sizes, header/data split, timeouts, region id, device, and optional overlay. `struct fpga_manager_ops` provides state/status, parse header, write init, contiguous/scatter write, write complete, remove, and sysfs groups. `fpga_mgr_load()` runs the load sequence: request/parse/init/write/complete, using ops and updating state. Registration APIs include normal, full, and devm variants with module-owner wrappers.

## State and dependencies
`struct fpga_manager` embeds a device, reference mutex, current state, compatibility id, ops/module owner, and private data. Dependencies include platform/device core, mutexes, scatter-gather tables, firmware loading, and module lifetime.

## Integration, risks, and tests
FPGA regions and low-level platform drivers rely on this API. Risks include inconsistent state transitions, missing `write_sg` or `write` handling, header size/data size confusion, timeout misuse, incompatible images, and module unload during programming. Tests should cover registration/devm cleanup, full and partial loads, parse-header `-EAGAIN`, buffer vs scatter input, status error bits, lock exclusion, and remove-state callbacks.
