## sources/distributed-fs/beegfs/meta/source/program/Program.h

Purpose: declares the static `Program` facade for the metadata server process and exposes the current `App` singleton-like pointer.

Important APIs/types: `Program::main(int argc, char** argv)` is the bootstrap entry. `Program::getApp()` returns the static `App*`. The constructor is private to prevent instances.

Control flow: external code does not instantiate `Program`; it calls static methods only. Many subsystems use `Program::getApp()` to access `Config`, `MetaStore`, work queues, sessions, and disposal directories.

State and persistence behavior: no persistence, but `Program::app` is global process state and effectively a service locator.

Dependencies and integration points: includes `<app/App.h>`. This creates broad coupling from storage/session code back to application-level services.

Risks: raw global pointer makes lifetime assumptions implicit. Tests using code that calls `Program::getApp()` need a real or mocked `App` installed.

Test signals: compile and dependency tests should watch for unintended inclusion bloat and initialization-order issues around `Program::app`.
