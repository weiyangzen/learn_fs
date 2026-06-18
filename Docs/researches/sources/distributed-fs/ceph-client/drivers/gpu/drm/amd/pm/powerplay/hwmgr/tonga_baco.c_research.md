# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.c

Purpose: implements BACO state transitions for Tonga/Iceland-family SMU7-era ASICs using hardware command tables.

Important APIs and functions: `tonga_baco_set_state()` is the exported transition routine. Static `baco_cmd_entry` tables sequence GPIO isolation, framebuffer request rejection, BCLK switching, SPLL/MPLL and memory clock shutdown, BACO entry through `BACO_CNTL`, BACO exit, and BIOS scratch cleanup. Topaz/Iceland uses reduced GPIO and alternate exit/clean tables.

Control flow and state: the function reads current state via `smu7_baco_get_state()` and returns success when already in the target state. Entry programs GPIO, FB request/reject, BCLK, PLL shutdown, and enter tables. Exit sleeps 20 ms for regulator timing, then programs chip-specific exit and clean tables. No driver-side state is stored; hardware registers hold BACO state.

Dependencies and integration: depends on `amdgpu.h`, `tonga_baco.h`, generated GMC/BIF/DCE/SMU register headers, `common_baco` command types, `baco_program_registers()`, and `smu7_baco_get_state()`.

Risks and test signals: table ordering and wait masks are hardware-critical; `BACO_CNTL__PWRGOOD_MASK` uses addition rather than bitwise OR; command-table return conventions are non-obvious; the 20 ms exit delay is fixed. Test enter/exit on Tonga and Topaz/Iceland, repeated idempotent calls, runtime PM/suspend cycles, PLL/memory restoration, and failure-path logging.
