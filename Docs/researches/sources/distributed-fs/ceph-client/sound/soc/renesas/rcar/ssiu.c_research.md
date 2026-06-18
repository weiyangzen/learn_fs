# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ssiu.c

## Purpose

`ssiu.c` implements the Serial Sound Interface Unit, especially BUSIF configuration, TDM/multi-SSI mode bits, HDMI lane selection, BUSIF error interrupt/status handling, DMA channel requests, and compatibility mapping between old SSI-only DTs and explicit `rcar_sound,ssiu` nodes.

## Important APIs, types, and functions

`struct rsnd_ssiu` stores the module, per-BUSIF lifecycle status, user count, hardware SSI ID, and BUSIF sub-ID. `rsnd_ssiu_probe()` allocates modules either from explicit SSIU children or from SSI count for compatibility, chooses Gen1 or Gen2-style ops, and maps flat child indices to `(id,id_sub)` using generation tables. `rsnd_parse_connect_ssiu()` connects explicit SSIU phandles or compatible BUSIF0 modules. `rsnd_ssiu_init()` configures SSI mode registers and error interrupts. `rsnd_ssiu_init_gen2()` adds TDM mode, BUSIF ADINR/MODE/DALIGN setup, and HDMI selection. `rsnd_ssiu_start_gen2()`/`stop_gen2()` enable BUSIF and multi-SSI control. `rsnd_ssiu_busif_err_status_clear()` is called from SSI IRQ handling.

## Control Flow

Probe determines module count and ID callbacks based on generation and DT shape. Connection parsing prefers explicit SSIU nodes; otherwise DMA-mode SSI streams get BUSIF0 for backward compatibility. During init, SSIU clears previous BUSIF errors, configures `SSI_MODE0` for BUSIF use, sets sharing/synchronization bits for pin sharing and multi-SSI, enables BUSIF error interrupts, writes TDM extend/split mode, configures BUSIF registers if used, and selects HDMI output lanes when stream flags indicate HDMI. Start enables the selected BUSIF and, for multi-SSI, writes `SSI_CONTROL`. Stop disables BUSIF, decrements users, and clears multi-SSI control when the last user stops.

## State and Persistence Behavior

Per-BUSIF status is stored in `busif_status[]`, so lifecycle tracking is per sub-ID rather than per SSIU module object. `usrcnt` guards shared multi-SSI control teardown. Hardware mode and BUSIF registers are rebuilt at init.

## Dependencies and Integration Points

SSIU depends on SSI runtime state, core TDM/HDMI flags, BUSIF alignment helpers, DMA channel request helpers, pseudo-register mapping, and generation-specific BUSIF index tables. It is tightly coupled to SSI interrupt handling for overrun/underrun reporting.

## Risks and Test Signals

Risks include Gen2/Gen3/Gen4 flat-index mapping mistakes, SSI9 special BUSIF registers, shared-pin/multi-SSI bit combinations, user-count underflow, and compatibility behavior when DT lacks `rcar_sound,ssiu`. Tests should cover explicit and legacy DTs, BUSIF0-7 where supported, TDM extend and split modes, HDMI0/HDMI1 lane selection, multi-SSI start/stop, and BUSIF error IRQ clearing.
