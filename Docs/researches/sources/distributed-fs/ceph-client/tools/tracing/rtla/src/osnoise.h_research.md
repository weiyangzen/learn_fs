# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise.h

## Purpose
`osnoise.h` declares the osnoise/hwnoise parameter structure, sentinel constants, osnoise configuration APIs, command entry points, and external `tool_ops` tables.

## Important APIs, Types, and Functions
`enum osnoise_mode` distinguishes normal OS noise from hardware-related noise mode. `struct osnoise_params` embeds `struct common_params` and adds runtime, period, threshold, and mode. `to_osnoise_params()` converts a common pointer back to its container. Sentinel constants `OSNOISE_OPTION_INIT_VAL` and `OSNOISE_TIME_INIT_VAL` define invalid/uninitialized states. Prototypes cover context allocation, config get/set/restore, missed-event reporting, apply/enable, and command mains.

## Control Flow and Integration
The header lets top/hist mode files share the same apply/enable helpers. `rtla.c` reaches `osnoise_main()` and `hwnoise_main()`, while `timerlat.c` reuses timerlat-related osnoise setters.

## State and Persistence
The declared APIs manage tracefs-persisted osnoise settings and tool-local contexts that restore those settings on destruction.

## Dependencies and Integration Points
It includes `common.h`, which pulls in trace/action/util dependencies. It exposes `timerlat_top_ops`, `timerlat_hist_ops`, `osnoise_top_ops`, and `osnoise_hist_ops` across modules.

## Risks and Edge Cases
Sentinel semantics are part of the ABI between header and implementation; changing them can break restore logic. The container macro requires the `common` field to remain embedded in `struct osnoise_params`.

## Test Signals
Compile all osnoise/timerlat modes after changes and validate that default top/hist command dispatch still links against the declared ops.
