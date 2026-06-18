# sources/cloud-native/containerd/api/buf.yaml

## Purpose
This Buf module config declares the containerd API module and dependency set.

## Important APIs, Types, And Functions
It uses version `v2`, depends on `buf.build/googleapis/googleapis`, and defines module path `.` with name `buf.build/containerd/api-dev`.

## Control Flow
Buf commands in the Makefile and workflows read this file for dependency resolution, module identity, build, format, generate, and breaking checks.

## State And Persistence
Policy state is stored in YAML; Buf dependency updates may affect lock/dependency files elsewhere.

## Dependencies And Integration Points
It integrates with `buf.gen.yaml`, `buf-breaking.yml`, and API proto imports such as Google API protos.

## Risks
Changing module name or deps can alter breaking-check baseline and generation resolution.

## Test Signals
`buf build`, `buf format --diff --exit-code`, and PR breaking checks validate this file.
