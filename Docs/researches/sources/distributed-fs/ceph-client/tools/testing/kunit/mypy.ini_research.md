<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/mypy.ini -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/mypy.ini

## Purpose

`mypy.ini` defines the static type-checking policy for KUnit's Python tooling. It opts into strict mypy checking while preserving compatibility with Python versions older than 3.9.

## Important APIs, Types, and Functions

The file is configuration, not executable code. The `[mypy]` section sets `strict = True`, enabling mypy's broad family of strictness checks. It also sets `disable_error_code = type-arg`, allowing annotations that omit newer generic type arguments such as `subprocess.Popen[str]`.

## Control Flow

There is no runtime control flow. `run_checks.py` invokes `mypy --config-file mypy.ini --exclude _test.py$ --exclude qemu_configs/ .`, so this file controls type checking for production KUnit Python modules while excluding tests and architecture snippets.

## State and Persistence Behavior

The file persists local type-checking policy only. It does not create cache state itself, although mypy may create its own cache when invoked by developer tooling.

## Dependencies and Integration Points

It depends on the installed `mypy` executable and integrates with `run_checks.py`. The disabled `type-arg` error reflects the KUnit tool's desire to support Python 3.7+ syntax while still benefiting from strict type checks elsewhere.

## Risks and Edge Cases

Disabling `type-arg` weakens strict coverage for generic types and can hide imprecise container or subprocess annotations. Conversely, strict mode may reject changes that are runtime-correct but under-annotated. The exclusion of `qemu_configs/` means architecture config modules receive less type-check scrutiny.

## Test Signals

The main signal is a successful `mypy --config-file mypy.ini --exclude _test.py$ --exclude qemu_configs/ .` run from the KUnit tool directory. Regressions appear as new strict typing failures or use of syntax that breaks the Python versions the tool still supports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/mypy.ini -->
