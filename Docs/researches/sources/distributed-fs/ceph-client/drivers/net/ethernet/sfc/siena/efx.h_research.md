# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx.h

## Purpose
Shared internal Siena API header for TX, RX, filters, ethtool, MTD, XDP, and lifecycle code.

## Important APIs and definitions
Declares TX entry points, RX delivery functions, queue size constants, filter wrappers, RSS helpers, ethtool ops, IRQ moderation APIs, software stats, optional MTD helpers, SR-IOV VF sizing, device detach/attach helpers, reset-lock assertion helper, and XDP TX buffer submission.

## Control flow and integration
Functions are implemented across sibling source files. Inline wrappers dispatch through `efx->type` callbacks for TX enqueue and filter operations, with indirect-call optimization for TX enqueue.

## State and persistence behavior
No state is stored here. Helpers operate on NIC, channel, queue, filter, XDP, and netdev state owned elsewhere.

## Dependencies
Depends on `net_driver.h`, `filter.h`, MCDI RSS constants, indirect-call support, and optional MTD/SR-IOV config symbols.

## Risks
Inline wrappers assume NIC type callbacks are valid. Queue sizing macros must remain aligned with hardware descriptor limits. Detach/attach helpers must wrap disruptive operations to avoid TX scheduler races.

## Test signals
Compile all optional configs and exercise TX/RX, filter operations, queue resizing, XDP TX, reset, and MTU-change paths.
