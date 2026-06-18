<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_low_i2c.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_low_i2c.h

## Purpose
This header declares the low-level PowerMac I2C bus API used by platform functions and drivers that need direct access to Mac I2C controllers.

## Important APIs, Types, And Functions
It defines bus type, mode, flags, and transfer direction enums; forward declares `struct pmac_i2c_bus` and `struct i2c_adapter`; and declares initialization, bus lookup, address extraction, controller/bus node/type/flag/channel accessors, adapter conversion/matching helpers, open/close, mode setting, transfer, and platform-function suspend/resume APIs.

## Control Flow
Callers find a bus from device-tree or adapter, open it optionally in polled mode, set a transfer mode, execute `pmac_i2c_xfer()` with address direction, subaddress size, buffer and length, then close the bus. Suspend/resume hooks coordinate platform-function users.

## State And Persistence Behavior
Bus state is owned by the implementation: open/closed state, mode, controller node, channel, flags, and adapter linkage. Hardware I2C controller state persists until closed or reprogrammed.

## Dependencies And Integration Points
It integrates with PowerMac device tree, Linux I2C adapters, platform functions, thermal/PMU/SMU-related devices, and suspend/resume.

## Risks And Edge Cases
Polled mode is needed in early or atomic contexts. Address direction and subaddress size must match device protocol. Failing to close or restore mode can block shared bus users.

## Test Signals
Probe PowerMac I2C devices, test adapter matching, reads/writes with all supported modes, polled transfers, suspend/resume, and bus sharing across clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_low_i2c.h -->
