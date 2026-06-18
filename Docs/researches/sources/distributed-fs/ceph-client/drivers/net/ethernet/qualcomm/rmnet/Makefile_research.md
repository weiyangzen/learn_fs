<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Makefile

## Purpose
The rmnet Makefile defines the object composition of the RMNET MAP module.

## Important APIs, Types, and Data
- `rmnet-y` includes `rmnet_config.o`, `rmnet_vnd.o`, `rmnet_handlers.o`, `rmnet_map_data.o`, and `rmnet_map_command.o`.
- `obj-$(CONFIG_RMNET) += rmnet.o` builds the aggregate module when enabled.

## Control Flow
Kbuild combines the listed objects into `rmnet.o` according to `CONFIG_RMNET`. There is no runtime control flow here.

## State and Persistence
The file controls build graph state only.

## Dependencies and Integration Points
Consumes the Kconfig symbol and includes config, virtual device, handler, data MAP, and command MAP implementation files.

## Risks and Edge Cases
Adding a new rmnet source file requires this list to be updated. Removing an object that owns exported internal symbols will cause link failures or missing functionality.

## Test Signals
Building RMNET as a module and built-in should link all listed objects and expose the `"rmnet"` rtnl link kind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Makefile -->
