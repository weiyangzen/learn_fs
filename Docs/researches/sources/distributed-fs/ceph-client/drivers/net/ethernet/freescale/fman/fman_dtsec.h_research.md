# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_dtsec.h

## Purpose

`fman_dtsec.h` is the narrow declaration header for the dTSEC MAC backend. It includes the shared FMan MAC definitions and exposes `dtsec_initialization()` to the MAC device probing layer.

## Important APIs, Types, And Functions

The only API is `int dtsec_initialization(struct mac_device *mac_dev, struct device_node *mac_node, struct fman_mac_params *params);`. `struct mac_device` is forward-declared, while `struct fman_mac_params` and callback types come from `fman_mac.h`.

## Control Flow

Callers allocate and populate a generic `mac_device`, parse the FMan MAC device-tree node, prepare `fman_mac_params`, and then call `dtsec_initialization()`. The implementation fills operation pointers, configures registers, resolves PCS resources, and registers FMan interrupt callbacks.

## State And Persistence Behavior

No state is stored in the header. It creates a compile-time contract that `mac_dev->fman_mac` will be initialized and owned by the dTSEC implementation on success.

## Dependencies And Integration Points

This header integrates `fman_dtsec.c` with the generic FMan MAC probing code. It depends on `fman_mac.h` and Linux device-tree types through the function signature.

## Risks And Edge Cases

The contract does not describe ownership or cleanup semantics; callers must rely on the implementation and surrounding MAC framework. Since only one function is exposed, any signature change requires updates to the generic MAC factory code.

## Test Signals

Compile all dTSEC-enabled configurations and verify the generic MAC probe can include this header without circular dependencies. Probe tests should exercise successful and deferred PCS lookup paths.
