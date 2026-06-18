# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/sec2.rs

## Purpose

`falcon/sec2.rs` defines the Falcon engine marker for the SEC2 security processor, which Nova uses to run Booter firmware during GSP startup.

## Important APIs, Types, And Functions

`struct Sec2(())` implements `RegisterBase<PFalconBase>` at `0x00840000`, `RegisterBase<PFalcon2Base>` at `0x00841000`, and `FalconEngine`.

## Control Flow

The file has no runtime code beyond trait-associated constants. Generic `Falcon<Sec2>` methods use these base addresses for reset, firmware load, mailbox, and boot operations.

## State And Persistence Behavior

No software state is stored. The marker controls which SEC2 hardware registers are accessed, and any persistent hardware state is managed by generic Falcon routines.

## Dependencies And Integration Points

It depends on register-base traits and generic Falcon engine markers. It integrates with `BooterFirmware`, `Gpu`, and GSP boot code through `Falcon<Sec2>`.

## Risks And Test Signals

Risks are limited but severe if register bases are wrong. Test by resetting SEC2, loading booter firmware, receiving expected mailbox status, and confirming no GSP/Falcon register range is accidentally addressed.
