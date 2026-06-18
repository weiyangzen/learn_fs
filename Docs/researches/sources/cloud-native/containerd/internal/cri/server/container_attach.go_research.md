# sources/cloud-native/containerd/internal/cri/server/container_attach.go

## Purpose

This file implements CRI attach endpoint preparation and the internal callback that binds a streaming attach session to a running container task and its `ContainerIO`.

## Important APIs, Types, and Functions

`Attach` validates the container exists and is running, then asks the stream server for an attach URL. `attachContainer` is the streaming callback that receives client stdin/stdout/stderr, TTY mode, and resize events, loads the task, wires terminal resize, builds `cio.AttachOptions`, and calls `cntr.IO.Attach`.

## Control Flow

`Attach` gets the CRI container from `containerStore`, records tracing attributes, checks status, and returns `streamServer.GetAttach(r)`. `attachContainer` creates a cancellable context, validates container state again, loads the containerd task, starts resize handling that calls `task.Resize`, defines `CloseStdin` as `task.CloseIO(...WithStdinCloser)`, and blocks in `ContainerIO.Attach` until attach completes.

## State and Persistence Behavior

The method does not persist new state. It interacts with live task IO and terminal size state. Attach URLs are managed by the stream server.

## Dependencies and Integration Points

It depends on CRI runtime protobufs, containerd client task APIs, remotecommand terminal sizes, CRI IO package, stream server callbacks, and tracing.

## Risks and Edge Cases

State is checked both before URL creation and at attach time because the container can exit between calls. Resize errors are logged but do not terminate attach. `CloseStdin` must close runtime stdin only when attach semantics require it.

## Test Signals

Tests should cover missing container, non-running state, URL creation, attach callback state revalidation, resize propagation, stdin close behavior, and TTY stderr handling through `ContainerIO`.
