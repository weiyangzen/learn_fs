# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/enum.h

## Purpose
`enum.h` defines shared Falcon driver enumerations and masks for loopback modes and reset types. These values are used across ethtool self-tests, PHY/MAC configuration, reset scheduling, reset logging, and hardware recovery.

## Important APIs, Types, and Functions
`enum ef4_loopback_mode` assigns stable numeric IDs to no-loopback, datapath, MAC/internal, PHY, wireside, and external loopback modes. Macros such as `LOOPBACKS_INTERNAL`, `LOOPBACKS_WS`, `LOOPBACKS_EXTERNAL()`, `LOOPBACK_MASK()`, `LOOPBACK_INTERNAL()`, `LOOPBACK_EXTERNAL()`, `LOOPBACK_CHANGED()`, and `LOOPBACK_OUT_OF()` classify and compare modes. `LOOPBACK_TEST_MAX` limits which modes participate in self-tests. `enum reset_type` distinguishes reset methods/scopes from reset reasons such as watchdog, interrupt error, RX recovery, DMA error, and TX skip.

## Control Flow
The file contains no executable functions, but its masks drive branches in port reconfiguration, link settings, ethtool self-test enumeration, and reset scheduling. Reset methods are intentionally ordered by increasing scope, and `ef4_reset()` uses that ordering when clearing pending reset bits covered by a completed reset.

## State and Persistence
No state is stored here. Numeric enum values effectively become ABI-like internal constants for logs, string lookup tables, bitmasks, and pending reset bit positions, so changing them would affect runtime behavior across the driver.

## Dependencies and Integration Points
The definitions are consumed by `efx.c`, `ethtool.c`, PHY/MAC code, self-test code, and string-table helpers. The comments explicitly require loopback defines and enum values to stay synchronized.

## Risks
The loopback masks use `1 << mode`, so adding enough modes to exceed the width of `int` or failing to update masks will cause incorrect classification. Reset ordering is semantically significant; inserting new methods in the wrong location can cause `reset_pending` clearing bugs. `RESET_TYPE_INVSIBLE` is misspelled in the comment, but the enum constant is `RESET_TYPE_INVISIBLE`.

## Test Signals
Self-test string counts should include expected loopback modes, and loopback mode changes should drive PHY transmit-disable behavior correctly. Reset tests should verify that broader resets clear narrower pending reset bits while reason-based reset scheduling maps through NIC-type callbacks as expected.
