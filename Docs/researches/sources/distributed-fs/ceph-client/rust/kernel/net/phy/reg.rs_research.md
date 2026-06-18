# sources/distributed-fs/ceph-client/rust/kernel/net/phy/reg.rs

Purpose: provides sealed typed access to MDIO clause 22 and clause 45 PHY registers and a unified `Register` trait consumed by `Device`.

Important APIs/types/functions: sealed `Register`, `C22`, `Mmd`, `C45`, C22 standard register constants, `C22::vendor_specific`, MMD constants, `C45::new`, and `read_status` implementations for C22 and C45.

Control flow: `Device::read`/`write` call the selected register object's trait methods. C22 reads/writes open-code `phy_read`/`phy_write` through `mdiobus_read`/`mdiobus_write` using the PHY's bus and address. C45 reads/writes call `phy_read_mmd` and `phy_write_mmd`. `read_status` dispatches to `genphy_read_status` or `genphy_c45_read_status`.

State and persistence behavior: no module-owned state. Reads/writes affect hardware registers and PHYLIB-maintained status as the C helpers do.

Dependencies and integration points: depends on `super::Device`, kernel error conversion, `uapi` MDIO constants, and `build_assert!`. The sealed trait prevents external register namespace implementations that might violate assumptions.

Risks: C22 vendor-specific addresses are const-checked to 16..31; incorrect constants would target wrong hardware registers. Hardware I/O errors are converted through `to_result`. Clause 45 MMD device addresses are represented as `u8`, matching valid 5-bit values from constants.

Test signals: compile-time tests for valid/invalid vendor-specific addresses, unit tests for MMD constants, and hardware/mock integration tests verifying C22/C45 read/write errno handling and status helper dispatch.
