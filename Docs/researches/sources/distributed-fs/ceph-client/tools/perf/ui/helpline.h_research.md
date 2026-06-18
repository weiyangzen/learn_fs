# sources/distributed-fs/ceph-client/tools/perf/ui/helpline.h

## Purpose

`helpline.h` declares the generic perf helpline interface and shared buffers.

## Important APIs, Types, and Functions

`struct ui_helpline` contains `pop`, `push`, and `show` callbacks. The header declares `helpline_fns`, `ui_helpline__init`, all helpline wrapper functions, `ui_helpline__current[512]`, and `ui_helpline__last_msg[]`.

## Control Flow and State

There is no executable flow. The header defines the state that TUI and GTK backends mutate and generic callers consume.

## Dependencies and Integration Points

It is included by generic, TUI, GTK, and browser code.

## Risks and Test Signals

Risks are buffer-size assumptions and missing definitions when a backend is omitted. Build tests across UI configurations and runtime helpline smoke tests validate it.
