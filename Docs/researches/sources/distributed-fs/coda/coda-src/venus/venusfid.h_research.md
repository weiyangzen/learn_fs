# sources/distributed-fs/coda/coda-src/venus/venusfid.h

## Purpose
This header defines Venus-level fids, which extend Vice fids with a realm id, plus helper conversions among kernel fids, Vice fids, volume ids, and printable fid strings.

## Important APIs, Types, and Functions
`VenusFid` contains `Realm`, `Volume`, `Vnode`, and `Unique`; `Volid` contains `Realm` and `Volume`. Helpers include `VenusToKernelFid`, `KernelToVenusFid`, `MakeViceFid`, `MakeVolid`, `FID_EQ`, `FID_VolEQ`, `FID_IsVolRoot`, `FID_`, and `MakeVenusFid`. It defines `FakeRootVolumeId`, `FakeRepairVolumeId`, declares `FID_IsLocalFake`, and provides `FID_IsExpandedDir()` overloads.

## Control Flow
Most helpers are reinterpretation or inline field comparisons. `FID_()` alternates between two static buffers so two fid strings can appear in one expression. Fake/expanded directory helpers combine local fake realm checks with Vice fake-root tests.

## State and Persistence Behavior
Fids are value identifiers that are stored throughout persistent and transient Venus data structures. The helper casts rely on field layout: `Volume,Vnode,Unique` must match `ViceFid`, and the full struct must match `CodaFid` for kernel exchange.

## Dependencies and Integration Points
It depends on `codadir.h` for fid/realm/volume types and fake-root helpers. It integrates with kernel IPC, Vice RPC arguments, realm-aware FSDB/VDB lookups, callback conversion, and local fake volumes.

## Risks and Test Signals
Risks include strict layout assumptions, static buffer reuse in `FID_()`, and type-punning aliasing. Tests should assert struct sizes/field offsets against kernel/Vice definitions, check conversion round trips, and cover fake root/repair fids across local and non-local realms.
