# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/platform.go

## Purpose
Implements Linux platform console handling for shim terminal IO using an epoller and optional pluggable logging binaries.

## Important APIs, Control Flow, And State
`NewPlatform` creates a console epoller and starts its wait loop. `linuxPlatform.CopyConsole` adds a console to epoll, optionally copies stdin from FIFO, parses stdout URI, and either starts a binary/binary-v2 logger with expected extra fds and readiness protocol or copies console output to a FIFO. It returns an epoll console for resize/shutdown. `ShutdownConsole` asserts `EpollConsole` and closes through the epoller; `Close` closes the epoller. State includes epoll fd, FIFOs, OS pipes, logger processes, copy goroutines, and wait groups.

## Dependencies And Integration
Uses console, fifo, stdio platform interface, namespaces, and process logging command helpers. It is used by `process.Init` and `process.Exec` terminal create paths.

## Risks And Test Signals
Risks include epoller lifecycle leaks, logger readiness failures, FIFO open blocking, fd ordering contract breaks, and shutdown type assertion errors. Tests should cover platform initialization, binary-v2 readiness, FIFO console copy, stdin shutdown, epoller close, and error cleanup.
