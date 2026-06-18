# File Research: sources/block-storage/stratisd/src/engine/strat_engine/metadata/mod.rs

## Purpose

`metadata/mod.rs` is the public module facade for Stratis metadata support. It defines the `bytes!` helper macro, declares metadata submodules, and re-exports the metadata types and functions used elsewhere in the engine.

## Contents

- Defines `bytes!($number)` to convert a sector count into bytes via `devicemapper::SECTOR_SIZE`.
- Declares private submodules:
  - `bda`
  - `mda`
  - `sizes`
  - `static_header`
- Re-exports:
  - `BDA`
  - `BlockdevSize`
  - `MDADataSize`
  - `device_identifiers`
  - `disown_device`
  - `static_header`
  - `MetadataLocation`
  - `StaticHeader`
  - `StaticHeaderResult`
  - `StratisIdentifiers`

## Role

This file keeps the metadata subsystem’s internal layout private while exposing the stable engine-facing API for BDA handling, static-header discovery/repair, and selected size types.
