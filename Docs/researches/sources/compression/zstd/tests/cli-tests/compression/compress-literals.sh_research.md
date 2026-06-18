# sources/compression/zstd/tests/cli-tests/compression/compress-literals.sh

## Purpose

This CLI test verifies explicit literal compression mode toggles across normal and fast compression levels.

## Important APIs, Types, and Functions

It pipes compressed output into `zstd -t` for `--no-compress-literals` at `-1`, `-19`, and `--fast=1`, and for `--compress-literals` at `-1` and `--fast=1`.

## Control Flow, State, and Persistence

`set -e` fails on any invalid output or CLI failure. No files are created because all outputs use stdout.

## Dependencies and Integration Points

It targets `literalCompressionMode` parsing in `zstdcli.c` and the zstd compression parameter passed into file I/O.

## Risks and Test Signals

Signals are that both forced modes produce decodable frames across selected strategies. The test does not assert ratio or whether literals were actually encoded as requested beyond successful parameter acceptance.
