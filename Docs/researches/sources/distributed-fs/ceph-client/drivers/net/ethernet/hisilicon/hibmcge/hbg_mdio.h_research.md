
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_mdio.h

## Purpose

This header declares HIBMCGE MDIO/PHY lifecycle and NP-link repair helpers.

## Important APIs, Types, and Functions

It declares `hbg_mdio_init()`, `hbg_phy_start()`, `hbg_phy_stop()`, and `hbg_fix_np_link_fail()`.

## Control Flow

No control flow is present.

## State and Persistence

No state is declared here.

## Dependencies and Integration Points

The declarations connect main netdev lifecycle and service work to MDIO/PHY implementation.

## Risks and Edge Cases

Prototype mismatch would break probe/open/stop or NP-link service integration.

## Test Signals

Build coverage and PHY lifecycle behavior validate the header.
