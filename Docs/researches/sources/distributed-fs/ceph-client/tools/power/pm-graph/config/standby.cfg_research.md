# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby.cfg

## Purpose
Provides a sleepgraph configuration file for the generic S1 standby preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: standby` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses standby mode with default-style low overhead tracing and no dev/callgraph/proc output.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
