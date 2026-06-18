# sources/control-plane/mayastor/io-engine/src/core/share.rs

## Purpose
Defines protocol-neutral share/unshare/update properties and the async `Share` trait for exposing bdev-backed volumes over NVMe-oF.

## Important APIs, Types, and Functions
- `Protocol::{Off, Nvmf}` maps from gRPC integer values and displays protocol names.
- `ShareProps::Nvmf`, `NvmfShareProps`, `UnshareProps`, `PtplProps`, and `UpdateProps` carry share configuration.
- `NvmfShareProps` supports controller ID range, ANA, allowed hosts, and PTPL path.
- `Share` trait defines `share_nvmf`, `create_ptpl`, `update_properties`, `unshare`, `shared`, `share_uri`, `allowed_hosts`, and bdev URI accessors.

## Control Flow and State
This file is mainly contracts and property conversion. `Protocol::try_from` validates user-supplied gRPC enum values. `From<Option<_>>` defaults missing props. Conversions from share props to update props preserve allowed hosts. Implementors perform actual target creation, PTPL file creation, property updates, and unsharing.

State lives in implementors and NVMe-oF subsystems, not in this file. PTPL props refer to a persistent JSON reservation path.

## Dependencies and Integration Points
Uses `async_trait` and `LvsError`. Implemented by logical volume/bdev share layers and consumed by replica and nexus gRPC handlers.

## Risks and Test Signals
`ShareProps::allowed_hosts(self)` consumes the enum, which is appropriate for conversion but can surprise callers. Only NVMe-oF is currently represented; previous iSCSI enum value is rejected. Tests should cover protocol validation, default props, allowed-host conversions, PTPL path propagation, and implementor behavior around persistent unshare.
