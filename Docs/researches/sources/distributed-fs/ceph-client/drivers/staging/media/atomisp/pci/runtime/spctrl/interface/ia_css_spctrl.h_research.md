# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/spctrl/interface/ia_css_spctrl.h

## Purpose

`ia_css_spctrl.h` is the public host-side interface for controlling AtomISP scalar processor firmware. It defines the firmware-load configuration contract and declares lifecycle/query entry points used by CSS code to load SP code into DDR/HMM memory, program SP control registers, start firmware execution, unload firmware storage, and inspect SP state.

## Important APIs, Types, and Functions

`ia_css_spctrl_cfg` is the central configuration structure. It carries firmware layout data (`code`, `code_size`, `ddr_data_offset`), SP DMEM layout (`dmem_data_addr`, `dmem_bss_addr`, `data_size`, `bss_size`), SP-control DMEM symbol addresses (`spctrl_config_dmem_addr`, `spctrl_state_dmem_addr`), the SP entry point, and a simulation-oriented `program_name`.

Declared APIs are `ia_css_spctrl_load_fw()`, `sh_css_spctrl_reload_fw()`, `get_sp_code_addr()`, `ia_css_spctrl_unload_fw()`, `ia_css_spctrl_start()`, `ia_css_spctrl_stop()`, `ia_css_spctrl_get_state()`, and `ia_css_spctrl_is_idle()`. The header also imports `ia_css_spctrl_comm.h`, which defines the SP-visible DMEM initialization structure and software-state enum.

## Control Flow

Higher-level CSS initialization fills an `ia_css_spctrl_cfg` from firmware metadata and calls `ia_css_spctrl_load_fw(SP0_ID, &cfg)`. After the hardware is ready, `ia_css_spctrl_start()` writes the DMEM init descriptor and toggles SP run/start bits. Reload paths use `sh_css_spctrl_reload_fw()` to reprogram the icache base when firmware has already been staged. Unload frees the host-side firmware copy. State and idle queries support lifecycle checks around firmware startup/shutdown.

## State and Persistence Behavior

The header does not own state, but its API describes state retained by `spctrl.c`: per-SP firmware code address, code size, entry point, DMEM config, SP DMEM control-symbol addresses, loaded flags, and optional program name. No file-backed persistence exists; firmware state is in HMM/DDR memory and SP hardware registers until unloaded, overwritten, or hardware reset.

## Dependencies and Integration Points

This interface depends on AtomISP system-global definitions for `sp_ID_t` and `ia_css_ptr`, CSS error conventions, and the communication ABI in `ia_css_spctrl_comm.h`. Local integration is visible in `sh_css.c`, where `sh_css_setup_spctrl_config()` prepares the config and `ia_css_spctrl_load_fw()` loads SP0 firmware during CSS initialization.

## Risks and Edge Cases

The header declares `ia_css_spctrl_stop()`, but no definition appears in the local AtomISP PCI subtree, so consumers calling it would fail to link unless another build variant supplies it. The config contains raw firmware pointers and firmware-generated DMEM addresses, making it sensitive to stale metadata, alignment mistakes, and host/SP ABI drift. `program_name` is mutable `char *` even though it is described as simulation-only metadata.

## Test Signals

Compile/link checks should verify every declared API has a definition in the selected build. Firmware-load tests should use valid and invalid SP IDs, null configs, misaligned `ddr_data_offset`, zero or oversized code sizes, and reload/unload/start sequencing. ABI tests should compare `ia_css_spctrl_cfg` fields against firmware metadata generated for the target ISP platform.
