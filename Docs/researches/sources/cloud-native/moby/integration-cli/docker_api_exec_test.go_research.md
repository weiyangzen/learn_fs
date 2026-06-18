# sources/cloud-native/moby/integration-cli/docker_api_exec_test.go

## Purpose
Integration tests for exec create/start/inspect lifecycle and cleanup.

## Important APIs and Types
Defines tests for missing command, invalid content type, paused containers, start modes, headers, repeated start errors, detach, valid/invalid commands, and exec state cleanup. Helpers include `createExec`, `createExecCmd`, `startExec`, `inspectExec`, `waitForExec`, and `inspectContainer`.

## Control Flow, State, and Persistence
Tests create running containers, create exec instances, start them through raw API/client paths, inspect exec state, wait for completion, and verify cleanup after container removal. They assert response headers, error messages, and container/exec state transitions.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on container lifecycle, exec API, request helpers, and polling. It mutates container exec state in daemon memory/persistence. Risks include races around cleanup and output timing, plus platform command differences. The suite signals exec API compatibility and resource cleanup.
