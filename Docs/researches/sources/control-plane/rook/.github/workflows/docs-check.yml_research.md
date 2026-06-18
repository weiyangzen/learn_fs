# sources/control-plane/rook/.github/workflows/docs-check.yml

## Purpose

Validates markdown style, generated docs, generated CRD docs, and mkdocs build output.

## Important APIs, Types, and Functions

The `docs-check` job sets up Go 1.26 and Python 3.9, runs `DavidAnson/markdownlint-cli2-action` against `Documentation/**/*.md` excluding Helm charts, then runs `make gen.docs`, `make generate-docs-crds`, `make docs-build`, and validation/diff checks.

## Control Flow

After checkout and tool setup, markdownlint checks docs style. Generated Helm docs are validated with `validate_modified_files.sh docs`. CRD docs are regenerated and compared with `git diff --ignore-matching-lines='on git commit'`. Finally mkdocs builds in strict mode.

## State and Persistence Behavior

Generated docs are runner-local. Dirty generated docs or CRD docs fail the job rather than persisting changes.

## Dependencies and Integration Points

It integrates with `.markdownlint-cli2.cjs`, custom markdownlint rules, Makefile docs targets, `build/release/Makefile` docs deps, mkdocs config, and generated CRD docs templates.

## Risks and Edge Cases

Ignoring lines containing `on git commit` is deliberate but can hide only that class of generated timestamp/hash noise. Python and mkdocs dependency changes can break docs without code changes.

## Test Signals

Passing means docs are lint-clean, generated docs are current, CRD docs are reproducible, and mkdocs can build the site.
