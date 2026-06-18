# sources/control-plane/rook/checkmake.ini

## Purpose

Configures CheckMake's maximum recipe body length rule for the root Makefile.

## Important APIs, Types, and Functions

The file has a `[maxbodylength]` section setting `maxBodyLength = 8`.

## Control Flow

CheckMake reads this file when linting Makefile targets and applies the body-length threshold.

## State and Persistence Behavior

No state is written.

## Dependencies and Integration Points

It integrates with `checkmake.yaml`, `Uno-Takashi/checkmake-action`, and the Makefile `lint.make` target.

## Risks and Edge Cases

The low threshold encourages short targets but can require exceptions or refactors for legitimate multi-step recipes.

## Test Signals

Passing CheckMake means Makefile recipes satisfy this and other CheckMake rules.
