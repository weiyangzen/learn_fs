# sources/distributed-fs/ceph-client/sound/soc/codecs/wm_hubs.h

## Purpose

`wm_hubs.h` declares the shared state and exported helper API for Wolfson WM899x hub analogue support implemented in `wm_hubs.c`. Codec drivers include it to embed the required private data and add common controls/routes/power helpers.

## Important APIs, Types, and Functions

- `struct wm_hubs_data`: required first member of the owning codec private data. It holds DC-servo settings/cache controls, Class W callback, micbias delays, lineout mode/state flags, DCS IRQ/completion state, and component pointer.
- Exported setup functions: `wm_hubs_add_analogue_controls`, `wm_hubs_add_analogue_routes`, and `wm_hubs_handle_analogue_pdata`.
- Runtime helpers: `wm_hubs_dcs_done`, `wm_hubs_vmid_ena`, `wm_hubs_set_bias_level`, and `wm_hubs_update_class_w`.
- Exported controls/data: `wm_hubs_spkmix_tlv`, `wm_hubs_hpl_mux`, and `wm_hubs_hpr_mux`.

## Control Flow

The header defines no executable flow. It establishes the call sequence expected by codec drivers: initialize private data, register common controls and routes, apply analogue platform data, route DCS done IRQs to `wm_hubs_dcs_done`, and call VMID/bias/Class W helpers from codec power paths.

## State and Persistence Behavior

The persistent state is `struct wm_hubs_data`. Its first-member layout requirement allows shared helper code to retrieve hub state directly from component drvdata even when the concrete codec private object is larger.

## Dependencies and Integration Points

The header depends on Linux completion, interrupt, list, and ALSA control declarations. It forward-declares `struct snd_soc_component` for the exported helper signatures. It integrates with WM899x codec drivers and their DAPM/bias/IRQ code.

## Risks and Edge Cases

- Violating the first-member requirement will corrupt all helper state access.
- Callers must initialize/add routes before relying on DCS cache and completion fields.
- Optional fields such as `check_class_w_digital` and `dcs_done_irq` alter behavior and must match the concrete chip.

## Test Signals

Compile coverage from WM899x users validates declarations. Runtime signals are the same as `wm_hubs.c`: successful helper setup, DCS IRQ completion, correct bias behavior, lineout mode programming, and Class W updates.
