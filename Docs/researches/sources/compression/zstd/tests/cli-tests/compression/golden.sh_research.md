# sources/compression/zstd/tests/cli-tests/compression/golden.sh

## Purpose

This CLI test compresses the golden compression corpus recursively and validates the results, including target block size and a historical block-splitter corruption case.

## Important APIs, Types, and Functions

It copies `$ZSTD_REPO_DIR/tests/golden-compression/` into `golden/`, runs recursive forced compression with `--output-dir-mirror golden-compressed/`, tests the compressed tree, repeats with `--target-compressed-block-size=1024`, and finally tests `-19 --zstd=mml=7` for PR #3517 coverage.

## Control Flow, State, and Persistence

`set -e` stops on any failed compression or test. It creates `golden/` and `golden-compressed/` trees.

## Dependencies and Integration Points

It depends on the golden corpus, recursive CLI support, mirrored output directories, and zstd test mode.

## Risks and Test Signals

The corpus path must exist. Signals are recursive mirroring, valid frames for all corpus files, target compressed block sizing not corrupting data, and regression coverage for the block splitter/min-match case.
