# File Research: sources/block-storage/kvdo/vdo/buffered-reader.h

## Purpose

Declares the opaque buffered reader API.

## Contents

- Forward declarations for `buffered_reader`, `dm_bufio_client`, and `io_factory`.
- Construction/destruction functions.
- `read_from_buffered_reader()`.
- `verify_buffered_data()`.

## Role

Provides sequential region reads without exposing dm-bufio state to callers.
