# sources/compression/xz/src/liblzma/simple/simple_coder.h

## Purpose
Declares encoder and decoder initialization entry points for all simple/BCJ filters.

## Important APIs, Types, And Functions
Declares paired init functions for x86, PowerPC, IA-64, ARM, ARM-Thumb, ARM64, SPARC, and RISC-V encoders and decoders.

## Control Flow
No runtime flow. This header centralizes init prototypes for filter registration code.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `common.h` for liblzma core types. Used by simple encoder/decoder property code, architecture filter files, and filter initialization tables.

## Risks
Prototype availability must match feature macro builds and implementation files. Missing declarations can break filter registration or cause conditional build drift.

## Test Signals
Build all filter combinations and verify each enabled filter can initialize both encoder and decoder chains.
