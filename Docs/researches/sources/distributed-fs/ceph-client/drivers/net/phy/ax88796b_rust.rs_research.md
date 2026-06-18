# sources/distributed-fs/ceph-client/drivers/net/phy/ax88796b_rust.rs

## Purpose
Provides a Rust reference implementation of the Asix PHY driver equivalent to `ax88796b.c`, using the Rust phylib abstractions.

## Important APIs, Types, and Functions
The module is registered by `kernel::module_phy_driver!` with `PhyAX88772A`, `PhyAX88772C`, and `PhyAX88796B`. It uses `kernel::net::phy::{Device, Driver, DeviceId}` and `reg::C22`. Important callbacks are `asix_soft_reset`, `PhyAX88772A::read_status`, `suspend`, `resume`, `soft_reset`, `link_change_notify`, and the simpler reset callbacks for AX88772C and AX88796B.

## Control Flow and State
The Rust reset helper writes `C22::BMCR` to zero then calls `genphy_soft_reset`, matching the C reset workaround. AX88772A status flow mirrors the C driver: update link, return if down, seed speed/duplex from BMCR, read LPA, and resolve autoneg if complete. Link-change notify ignores errors from `init_hw` and `start_aneg`, matching the best-effort C behavior. There is no private persistent state.

## Dependencies and Integration Points
Depends on `RUST_PHYLIB_ABSTRACTIONS`, the kernel Rust prelude, C UAPI constants, and the parent Makefile selecting this object when `CONFIG_AX88796B_RUST_PHY` is true. It exposes the same device IDs and module metadata shape through Rust macros.

## Risks and Test Signals
Risks include Rust abstraction behavior diverging from C phylib semantics, ignored errors in link-change notify hiding restart failures, and mismatched device-table/module names relative to the C implementation. Test signals include Rust-enabled kernel builds, module autoload for each device ID, behavior comparison against the C driver on AX88772A/AX88772C/AX88796B hardware, and reset/link renegotiation tests.
