# File Research: sources/block-storage/kvdo/vdo/buffered-writer.h

## Purpose

Declares the opaque buffered writer API.

## Contents

- Forward declarations for `buffered_writer`, `dm_bufio_client`, and `io_factory`.
- Construction/destruction functions.
- Data write, zero write, and explicit flush functions.

## Role

Provides sequential region writes while hiding block padding and dm-bufio lifecycle details.
