# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/enum.h

## Purpose
Defines Siena loopback mode and reset type enumerations plus helper masks.

## Important APIs and definitions
`enum efx_loopback_mode` enumerates internal, PHY, external, cross-port, and wireside loopbacks. `LOOPBACK_TEST_MAX` limits tested modes. Helper masks classify internal, wireside, and external loopbacks and detect loopback changes. `enum reset_type` separates reset methods/scopes from reset reasons such as watchdog, DMA error, MC failure, and MCDI timeout.

## Control flow and integration
Loopback constants drive MCDI link setup, self-tests, ethtool names, and MAC/PHY reconfiguration. Reset types drive scheduling, reason-to-method mapping, pending-bit clearing, and logging.

## State and persistence behavior
No runtime state is stored. Numeric constants become bit positions in masks like `efx->loopback_modes` and `efx->reset_pending`.

## Dependencies
Must remain consistent with firmware MCDI loopback numbering and string tables in common code.

## Risks
Changing enum values breaks firmware protocol mapping, ethtool output, loopback masks, and reset semantics. `RESET_TYPE_MCDI_TIMEOUT` is outside the ordered reset hierarchy and needs special handling.

## Test signals
Correct loopback self-test modes/names and reset logs/pending-bit behavior for every reset reason.
