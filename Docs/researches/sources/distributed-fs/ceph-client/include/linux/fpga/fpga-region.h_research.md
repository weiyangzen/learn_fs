# sources/distributed-fs/ceph-client/include/linux/fpga/fpga-region.h

## Purpose
This header defines FPGA regions, which coordinate a manager, compatibility id, image info, and bridge list for programming a portion of FPGA fabric.

## APIs, types, and control flow
`struct fpga_region_info` supplies a manager, optional compatibility id/private data, and optional `get_bridges()` callback. `struct fpga_region` embeds a device, mutex, bridge list, manager, image info, compatibility id, module owner, private data, and callback. `fpga_region_program_fpga()` is the orchestration entry point: it gathers/uses bridges, coordinates manager programming, and restores traffic. Registration APIs include full and compact macros that capture `THIS_MODULE`, plus class search and unregister.

## State and dependencies
Region state ties together bridge references, selected manager, image info, and exclusive region mutex. It depends on FPGA manager and bridge frameworks, device core, lists, modules, and optionally device tree/overlays through image info.

## Integration, risks, and tests
Regions are the policy layer for dynamic FPGA reconfiguration. Risks include programming with stale image info, bridge leaks on failure, compatibility-id mismatch, concurrent region programming, and module-owner lifetime bugs for `get_bridges`. Tests should cover registration/unregistration, class find matching, bridge acquisition failure rollback, successful program ordering, manager-load errors, and concurrent program exclusion.
