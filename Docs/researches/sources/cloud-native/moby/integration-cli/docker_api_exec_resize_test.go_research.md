# sources/cloud-native/moby/integration-cli/docker_api_exec_resize_test.go

## Purpose
Integration tests for exec resize API validation and race handling.

## Important APIs and Types
Defines `TestExecResizeAPIHeightWidthNoInt` and `TestExecResizeImmediatelyAfterExecStart`.

## Control Flow, State, and Persistence
Tests call exec resize endpoints with invalid non-integer height/width and resize immediately after exec start to catch races between exec lifecycle and TTY resize handling.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on exec API, request helpers, and running containers with TTY/exec sessions. Risks include timing sensitivity and platform TTY differences. Signals cover HTTP validation and daemon exec resize concurrency.
