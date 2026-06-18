# sources/compression/zstd/tests/cli-tests/dictionaries/setup_once

## Purpose
Suite-level fixture generation for dictionary CLI tests. It creates two intentionally different dictionaries and a sample input.

## APIs, control flow, and integration
The script sources platform helpers, creates `files/` and `dicts/`, generates seeds 1-50, trains `dicts/0`, generates seeds 51-100 into the same files directory, trains `dicts/1`, asserts the two dictionaries differ with `cmp ... && die`, and finally writes `files/0`.

## State, dependencies, risks, and test signals
Persistent suite state is `files/` and `dicts/`. Dependencies are `datagen`, `zstd --train`, `seq`, `cmp`, and `die`. Risks include nondeterministic or changed trainer behavior causing equal dictionaries or dictionary IDs. A pass creates the mismatch fixtures used by downstream tests.
