# sources/control-plane/longhorn-engine/integration/core/__init__.py

## Purpose
Marks `integration/core` as a Python package for pytest/import purposes.

## Important APIs, Types, and Functions
No code, APIs, or runtime declarations.

## Control Flow
No control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Enables package-style imports such as `from core.test_cli import bin` used by identity tests.

## Risks and Edge Cases
Empty package marker only; removal could affect imports depending on Python package discovery configuration.

## Test Signals
Its presence is indirectly validated by successful pytest collection/import.
