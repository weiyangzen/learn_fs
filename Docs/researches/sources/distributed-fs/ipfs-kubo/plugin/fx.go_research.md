<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/fx.go -->
# sources/distributed-fs/ipfs-kubo/plugin/fx.go

## Purpose

This file defines the interface for plugins that modify Kubo's Fx dependency graph.

## Important APIs, Types, and Functions

`PluginFx` embeds `Plugin` and adds `Options(core.FXNodeInfo) ([]fx.Option, error)`.

## Control Flow, State, and Integration

The loader registers each option function through `core.RegisterFXOptionFunc`. Implementations receive existing node info and usually append or decorate options.

## Dependencies, Risks, and Test Signals

Dependencies are Kubo core and Uber Fx. The interface is invasive and can destabilize node construction if plugins replace the wrong dependencies. Built-in `fxtest` and `nopfs` exercise the pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/fx.go -->
