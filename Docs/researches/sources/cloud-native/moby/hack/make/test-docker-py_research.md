# sources/cloud-native/moby/hack/make/test-docker-py

## Purpose
Runs Docker SDK for Python integration tests against the test daemon.

## Important APIs and Types
Uses Python test options, graphdriver settings, selected deselected tests, and integration daemon helpers.

## Control Flow, State, and Persistence
The script configures daemon graphdriver expectations, excludes known unsupported or incompatible SDK tests, starts the integration daemon through shared helpers, and runs the Python test suite with the configured environment.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Python test dependencies, a compatible daemon, and test certificates/environment. Risks include skipped tests hiding regressions, SDK test drift, and graphdriver-specific failures. CI docker-py bundle results are the direct signal.
