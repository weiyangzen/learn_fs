<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/tracer.go -->
# sources/distributed-fs/ipfs-kubo/plugin/tracer.go

## Purpose

This file defines the plugin interface for providing an OpenTracing tracer.

## Important APIs, Types, and Functions

`PluginTracer` embeds `Plugin` and adds `InitTracer() (opentracing.Tracer, error)`.

## Control Flow, State, and Integration

The loader calls `InitTracer` during injection and sets the returned tracer as the global OpenTracing tracer. The loader logs that tracer plugins are deprecated in favor of OpenTelemetry collector configuration.

## Dependencies, Risks, and Test Signals

Dependency is OpenTracing. Risks include process-global tracer mutation, deprecated API usage, and plugin initialization failure preventing injection. Loader tests or a sample tracer plugin would validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/tracer.go -->
