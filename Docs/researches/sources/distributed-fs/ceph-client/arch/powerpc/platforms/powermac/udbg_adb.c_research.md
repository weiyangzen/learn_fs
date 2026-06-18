
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/udbg_adb.c

Purpose: layers ADB keyboard input and optional BootX framebuffer text output onto the early `udbg` console used by xmon and early debugging on PowerMac.

Important APIs/functions/state: `udbg_adb_init_early()` can install BootX text output before full ADB probing. `udbg_adb_init()` captures existing `udbg_putc`, `udbg_getc`, and `udbg_getc_poll`, then replaces them with ADB-aware wrappers. `udbg_adb_getc_poll()` calls `pmu_poll_adb()` or `cuda_poll()` before delegating. With `CONFIG_BOOTX_TEXT`, `udbg_adb_local_getc()` waits for ADB keyboard keycodes, tracks shift state, maps keycodes through local tables, and draws a cursor via `btext`.

Control flow: initialization preserves the previous console implementation and uses this file as a final wrapper. It verifies a device-tree `keyboard` node whose parent is type `adb`, selects PMU or CUDA input by probing VIA controller helpers, and leaves BootX output active even if keyboard input is unavailable. Reads poll ADB and then either consume local xmon keycodes or delegate to the old console. Writes draw to BootX text and then delegate.

State and persistence: global callback pointers retain previous console state. `input_type`, `udbg_adb_use_btext`, `xmon_wants_key`, `xmon_adb_keycode`, and shift state are volatile early-debug state only.

Dependencies and integration points: integrates with global `udbg_*` callbacks, xmon ADB globals, BootX btext drawing, PMU/CUDA ADB polling, device-tree keyboard discovery, and PowerMac controller probes.

Risks: callback wrapping order is important because this implementation expects to be initialized last. Local keymap coverage is limited and ignores key-up transitions except for shift. Polling loops can spin indefinitely while waiting for input. Failure to find ADB input returns `-ENODEV` but may still change output callbacks.

Test signals: early xmon input from ADB keyboards, BootX text output, delegation to preexisting serial/other udbg console, PMU and CUDA keyboard polling, and no regressions when no ADB keyboard exists.
