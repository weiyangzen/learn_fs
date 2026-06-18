# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/cmd.c

## Purpose

`cmd.c` implements the R-Car CMD block, the command/routing stage that connects SRC output into CTU, MIX, and DVC processing. It exists only when DVC units are present and is attached by CTU, MIX, or DVC probe callbacks through `rsnd_cmd_attach()`.

## Important APIs, types, and functions

`struct rsnd_cmd` wraps an `rsnd_mod`. `rsnd_cmd_probe()` allocates one CMD module per DVC, initializes each module with `rsnd_cmd_ops`, and records `priv->cmd_nr`. `rsnd_cmd_attach()` connects a CMD module to a stream. `rsnd_cmd_init()` is the main hardware setup path: it computes `CMD_ROUTE_SLCT`, programs `CMD_BUSIF_MODE`, `CMD_BUSIF_DALIGN`, and invokes `rsnd_adg_set_cmd_timsel_gen2()`. `rsnd_cmd_start()` writes `CMD_CTRL = 0x10`; `rsnd_cmd_stop()` clears it. Debugfs can dump the per-CMD SCU register window.

## Control Flow

During CTU/MIX/DVC module probe, the caller attaches a CMD module with a matching ID. At stream init, CMD decides whether the stream uses MIX or only DVC. For MIX, it scans all DAIs and ORs route bits for every SRC feeding the same MIX, relying on the integrator to provide valid compatible paths. Without MIX it uses the current SRC ID and a static `cmd_case` table to choose the route. It then configures BUSIF shifting/alignment from common helpers and programs ADG timing for converted-rate operation. Start/stop are simple control-register toggles.

## State and Persistence Behavior

CMD has no private mutable runtime state beyond the generic `rsnd_mod` lifecycle status. Route state lives in hardware registers and is rebuilt at each init. Module allocation is devm-managed, but `rsnd_cmd_remove()` still calls `rsnd_mod_quit()` for clock/module cleanup symmetry.

## Dependencies and Integration Points

CMD depends on DVC count for allocation, CTU/MIX/DVC for attachment, SRC identity for route selection, `core.c` helpers for BUSIF shift and data alignment, ADG for timing selection, and `gen.c` for pseudo-register access. It is part of the SCU processing path and is sequenced after CTU/MIX/DVC for capture and before them for playback through the common module-order arrays.

## Risks and Test Signals

Risks include invalid DT routes, SRC IDs not covered by `path[]` or `cmd_case[]`, using MIX with incompatible SRC combinations, and capture/playback data alignment regressions. Test signals include successful playback/capture through DVC-only and MIX paths, debugfs route register dumps, SRC+DVC conversion tests, and negative tests for unsupported route IDs.
