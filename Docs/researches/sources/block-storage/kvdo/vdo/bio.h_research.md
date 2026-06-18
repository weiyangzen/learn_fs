# File Research: sources/block-storage/kvdo/vdo/bio.h

## Purpose

Declares VDO bio helper APIs and small inline wrappers.

## Contents

- Data copy functions.
- Inline conversion/completion helpers:
  - `vdo_get_bio_result()`,
  - `vdo_complete_bio()`.
- Bio allocation/free APIs.
- Bio statistics APIs.
- Async bio completion callback.
- Bio property and buffer reset APIs.

## Dependencies and Role

Wraps Linux block-layer details so VDO code can work in VDO status/geometry terms while still submitting normal kernel bios.
