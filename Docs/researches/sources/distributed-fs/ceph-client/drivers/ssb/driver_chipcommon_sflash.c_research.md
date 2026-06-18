# sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon_sflash.c

## Purpose
Serial flash detection for ChipCommon-backed SSB systems, preparing a platform device exposing flash memory metadata to the MTD stack.

## Important APIs, Types, and Functions
Defines `ssb_sflash_dev`, `ssb_sflash_resource`, flash ID tables for ST/SST/Atmel parts, internal `ssb_sflash_cmd`, and public `ssb_sflash_init`.

## Control Flow
Init switches on ChipCommon flash type. ST/SST probing issues deep-powerdown/release commands and reads IDs at flash addresses 0/1; Atmel probing reads status ID. It searches the corresponding table, fills `bus->mipscore.sflash` window/block/size/present fields, adjusts the platform resource end, and attaches platform data. The platform device is prepared but registered later by `main.c` after allocation services are ready.

## State and Persistence
Stores serial flash metadata in `struct ssb_sflash` and global platform device/resource fields. Hardware commands can affect flash power/read-ID state but do not modify flash contents.

## Dependencies and Integration Points
Called from `ssb_mips_flash_detect`, consumed by SSB device registration and MTD platform handling. Uses ChipCommon flash control/address/data registers.

## Risks
Unsupported IDs return `-ENOTSUPP`, preventing serial flash platform registration. Command polling is fixed at 1000 iterations with no sleep, so slow hardware may timeout. Global platform device/resource means multiple independent SSB serial flash instances would be problematic.

## Test Signals
Logs should identify flash name, size, block size, and count. MTD registration should see `ssb_sflash` with correct window and resource size; unsupported devices should fail without corrupting flash.
