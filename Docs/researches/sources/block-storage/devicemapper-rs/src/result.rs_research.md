# File Research: sources/block-storage/devicemapper-rs/src/result.rs

## Purpose
Defines the crate-wide result and outer error type.

## Key Types
`ErrorEnum` with `Error`, `Invalid`, and `NotFound`; `DmError` with `Dm(ErrorEnum, String)` and `Core(core::errors::Error)`; `DmResult<T>` alias.

## Behavior
Core errors convert into `DmError::Core`. Display distinguishes “DM Core error” from higher-level “DM error”.

## Notes
`DmError` implements `std::error::Error` but does not forward `source()` to core errors here.
