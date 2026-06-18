# File Research: sources/block-storage/kvdo/vdo/vdo-resume.h

## Purpose
Declares the internal preresume entry point.

## Public API
- `vdo_preresume_internal()`: applies new config and resumes a suspended VDO for a named device.

## Context
Called from device-mapper resume/preresume integration; resume itself cannot fail externally, so this function performs fail-able work beforehand.
