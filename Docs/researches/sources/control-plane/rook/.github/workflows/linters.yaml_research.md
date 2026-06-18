# sources/control-plane/rook/.github/workflows/linters.yaml

## Purpose

Runs YAML and Python linting plus Python formatting checks.

## Important APIs, Types, and Functions

Jobs are `yaml-linter`, which runs `make lint.yaml`, and `pylint`, which sets up Python 3.12, installs `pylint`, `requests`, and `pygit2`, runs `make lint.python`, then invokes `psf/black`.

## Control Flow

Push and PR triggers start both jobs with PR concurrency cancellation. Each checks out full history before running Makefile/action-based linting.

## State and Persistence Behavior

No persistent state is written. Python packages are installed in the ephemeral runner.

## Dependencies and Integration Points

It integrates with `Makefile` lint targets, `.yamllint`, Python scripts across the repo, and Mergify check names `yaml-linter` and `pylint`.

## Risks and Edge Cases

The `psf/black` action is invoked after pylint without explicit arguments; its exact default behavior matters. Installing `pylint` twice is redundant but harmless.

## Test Signals

Passing jobs indicate YAML files and Python scripts satisfy current lint and formatting gates.
