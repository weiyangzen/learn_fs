# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/spctrl/src/spctrl.c

## Purpose

`spctrl.c` implements the host-side scalar processor firmware controller for AtomISP CSS. It stages SP firmware into HMM/DDR memory, records the DMEM initialization contract, programs SP icache/start registers, starts SP execution, unloads staged firmware memory, and exposes simple state/idle queries.

## Important APIs, Types, and Functions

`struct spctrl_context_info` stores one SP's DMEM init descriptor, SP-control DMEM addresses, SP entry address, staged firmware HMM address, code size, and optional program name. The file keeps `spctrl_cofig_info[N_SP_ID]` and `spctrl_loaded[N_SP_ID]` as static per-SP state.

`ia_css_spctrl_load_fw()` validates inputs, copies firmware layout fields into `dmem_config`, allocates HMM memory for the firmware image, stores the image with `hmm_store()`, validates host pointer width and DDR data alignment, records the entry point and metadata, programs `SP_ICACHE_ADDR_REG`, invalidates icache, and marks the SP loaded. `sh_css_spctrl_reload_fw()` repeats the icache-base programming for preloaded firmware. `get_sp_code_addr()` returns the staged HMM address. `ia_css_spctrl_unload_fw()` frees staged firmware for a loaded SP. `ia_css_spctrl_start()` writes `dmem_config` into SP DMEM, writes `SP_START_ADDR_REG`, and sets `SP_RUN_BIT` and `SP_START_BIT`. `ia_css_spctrl_get_state()` reads the SP0 software-state symbol from DMEM. `ia_css_spctrl_is_idle()` reads the SP idle bit from `SP_SC_REG`.

## Control Flow

During CSS initialization, higher layers build an `ia_css_spctrl_cfg` and call `ia_css_spctrl_load_fw()`. The load path stages the full firmware blob in HMM memory, computes the DDR data address as `code_addr + ddr_data_offset`, and arms the SP instruction cache base. Once the hardware is idle and other CSS setup is complete, `ia_css_spctrl_start()` copies the init descriptor into the firmware-known SP DMEM address and starts the SP by programming control registers. Unload is a separate cleanup step that frees the staged code address only if the SP was marked loaded.

State queries are narrow. `ia_css_spctrl_get_state()` returns terminated for invalid SP IDs and only reads `sp_sw_state` for `SP0_ID`; other valid SP IDs return the initialized local default of zero. `ia_css_spctrl_is_idle()` asserts a valid ID and directly queries the hardware control register.

## State and Persistence Behavior

There is no persistent storage. Runtime state is static in the driver and per SP: staged HMM code address, firmware layout, entry point, DMEM control addresses, and loaded flag. Hardware state includes SP icache base/invalidation, DMEM initialization data, start address, and control-register run/start bits. Reload depends on the previously retained `code_addr`; unload resets only the code address and loaded flag, leaving other cached metadata intact.

## Dependencies and Integration Points

The file depends on HMM memory management, SP control and DMEM access helpers from `sp.h`, firmware ABI types from `ia_css_spctrl.h` and `ia_css_spctrl_comm.h`, CSS debug logging, and AtomISP platform constants such as `HIVE_ISP_DDR_WORD_BYTES`, `SP_ICACHE_ADDR_REG`, and `SP_SC_REG`. The primary local integration point is `sh_css.c`, which calls `ia_css_spctrl_load_fw()` while initializing CSS firmware.

## Risks and Edge Cases

The static array name is misspelled `spctrl_cofig_info`, which is harmless but easy to propagate. There is no locking around load, reload, unload, start, or query state. A second load for the same SP overwrites `code_addr` with `mmgr_NULL` before allocating a new blob, which can leak the previous staged firmware if called without unload. `get_sp_code_addr()` lacks SP-ID bounds checking. `sh_css_spctrl_reload_fw()` does not validate the SP ID or loaded flag. `ia_css_spctrl_get_state()` computes `HIVE_ADDR_sp_sw_state` from cached metadata but then ignores it and uses `sp_address_of(sp_sw_state)` for SP0, so the configured state address is not actually consulted in this build. The public header declares `ia_css_spctrl_stop()`, but this file does not define it.

## Test Signals

Tests should cover load/start/unload ordering, repeated load without unload, invalid SP IDs for every public function, null config handling, HMM allocation failure, pointer-size validation, `ddr_data_addr` alignment rejection, icache register programming on load and reload, DMEM descriptor contents written by start, state query for SP0 and non-SP0 IDs, and idle-bit reads. Build tests should catch the missing `ia_css_spctrl_stop()` definition if any caller starts using it.
