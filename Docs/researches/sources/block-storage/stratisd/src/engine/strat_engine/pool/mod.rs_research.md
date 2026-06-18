# File Research: sources/block-storage/stratisd/src/engine/strat_engine/pool/mod.rs

## Purpose

`pool/mod.rs` is the pool module facade. It declares pool implementation modules and re-exports the version-dispatch wrapper.

## Contents

- Declares:
  - `dispatch`
  - `inspection` behind `extras`
  - `v1`
  - `v2`
- Re-exports:
  - `AnyPool`

## Role

This file keeps pool implementation organization explicit while making `AnyPool` the main engine-facing pool type.
