# sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp.h

## Purpose

`wm_adsp.h` is the public ASoC-facing interface for the Wolfson/Cirrus ADSP support layer. It defines the embedding structure used by codec drivers, DAPM/control helper macros, firmware-file containers, exported lifecycle/control/compressed-stream APIs, and KUnit-only firmware lookup hooks.

## Important APIs, Types, and Functions

- `struct wm_adsp`: embeds `struct cs_dsp` and adds ASoC-specific state: part and firmware naming qualifiers, component pointer, firmware selection, optional/mandatory firmware policy, boot work, callbacks, preload/fatal flags, and compressed-stream/buffer lists.
- DAPM/control macros: `WM_ADSP1`, `WM_ADSP2_PRELOAD_SWITCH`, `WM_ADSP2`, and `WM_ADSP_FW_CONTROL` create standard widgets and controls wired to `wm_adsp.c` handlers.
- Firmware containers: `struct wm_adsp_fw_file` and `struct wm_adsp_fw_files` pair firmware pointers with allocated filenames.
- Lifecycle APIs: `wm_adsp1_init`, `wm_adsp2_init`, `wm_halo_init`, `wm_adsp2_remove`, component probe/remove helpers, DAPM event handlers, power/run/stop/hibernate APIs, and DSP clock setter.
- Compressed APIs: open/free/set_params/get_caps/trigger/IRQ/pointer/copy helpers for ALSA compressed streams.
- Control APIs: `wm_adsp_control_add`, `wm_adsp_write_ctl`, and `wm_adsp_read_ctl`.
- KUnit-only APIs: firmware file name lookup and request/release wrappers exposed when `CONFIG_KUNIT` is enabled.

## Control Flow

The header itself has no executable flow, but it defines the standard flow used by codec drivers. Drivers embed one or more `struct wm_adsp` objects, initialize them with the appropriate init function, add DAPM widgets/controls through macros, call component probe/remove helpers from codec component lifecycle, and wire DAPM events or IRQs to exported functions.

## State and Persistence Behavior

`struct wm_adsp` is persistent codec-private state. The embedded `cs_dsp` owns core firmware state and synchronization; the wrapper fields persist naming policy, firmware selection, preload behavior, fatal-error status, and stream lists. `struct wm_adsp_fw_files` is transient and must be released by the helper in `wm_adsp.c`.

## Dependencies and Integration Points

The header depends on Cirrus firmware core headers, ALSA SoC/DAPM/compress headers, and `wm_adsp.c` exports. It is consumed by codec drivers that include ADSP firmware cores and by KUnit tests for firmware lookup behavior.

## Risks and Edge Cases

- The comment states `struct wm_hubs_data` must be first in codec private data; here, `struct wm_adsp` has no such layout requirement, but callers must still ensure `snd_soc_component_get_drvdata` points to an array when using indexed macros.
- Macro shifts are used as DSP indices, so widget/control numbering must match the driver-owned array layout.
- KUnit-only prototypes are unavailable in normal builds.
- Compressed IRQ return values use integer constants, not `irqreturn_t`.

## Test Signals

Compile coverage from codecs using each macro is important. Runtime signals include correct DSP indexing from DAPM widget shifts, firmware enum controls mapping to the right `struct wm_adsp`, successful init/remove for ADSP1/ADSP2/Halo, and KUnit coverage of the exported firmware lookup helpers.
