# File Research: sources/block-storage/devicemapper-rs/src/consts.rs

## Purpose
Defines IEC binary-size constants under `IEC`.

## Key Exports
`Ki`, `Mi`, `Gi`, `Ti`, `Pi`, `Ei` as `u64`, each derived by multiplying by 1024.

## Behavior
Simple constants used throughout tests and device setup for loopback backing-file sizes, metadata sizes, and cache block bounds.

## Notes
Module intentionally allows non-snake-case and non-upper-case globals to preserve familiar IEC unit spelling.
