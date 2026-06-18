# sources/control-plane/longhorn-engine/integration/instance/__init__.py

## Purpose
This package initializer is empty. It exists to mark `integration/instance` as a Python package for imports and pytest discovery context.

## Important APIs, types, and functions
No APIs, types, functions, imports, or side effects are defined.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state is initialized or persisted.

## Dependencies and integration points
Its integration role is structural only: package recognition for tests such as `test_launcher_basic.py`.

## Risks and edge cases
Because it is empty, risk is limited to import/package layout. Removing it could affect Python versions or tooling that still rely on explicit package markers.

## Test signals
There are no direct test signals in this file; successful imports and pytest collection indirectly validate it.
