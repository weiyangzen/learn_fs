# File Research: sources/block-storage/kvdo/vdo/common.h

## Purpose

Defines small common UDS/VDO types and size constants.

## Contents

- Includes string utilities, type definitions, and `uds.h`.
- Defines:
  - `KILOBYTE`,
  - `MEGABYTE`,
  - `GIGABYTE`.
- Forward declares `struct uds_chunk_data`.
- Defines `struct uds_chunk_record` containing chunk name and chunk data.

## Role

Provides common definitions shared by UDS-related VDO code.
