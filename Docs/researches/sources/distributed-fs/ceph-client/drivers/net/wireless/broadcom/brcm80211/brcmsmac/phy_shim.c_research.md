# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy_shim.c

Purpose: Implements the two-way shim between the brcmsmac common driver and PHY code. It owns a small `phy_shim_info` wrapper containing `brcms_hardware`, `brcms_c_info`, and OS-private `brcms_info` pointers so PHY code can call driver, timer, interrupt, BMAC, SHM, template RAM, PLL, and object-memory services without seeing the full driver internals.

Important APIs: `wlc_phy_shim_attach()` allocates and initializes the shim with `kzalloc_obj(..., GFP_ATOMIC)`; `wlc_phy_shim_detach()` frees it. The `wlapi_*` functions are pass-through adapters for timers, interrupt masking, SHM read/write, maccontrol, core reset, MAC suspend/enable, bandwidth, TX antenna, PHY clocks, wake overrides, template RAM, rate SHM offset lookup, and object memory copies. `wlapi_ucode_sample_init()` is an intentional no-op placeholder.

Control flow and state: There is no independent persistent state beyond the three stored pointers. Every call immediately dereferences the shim and delegates to `brcms_*` or `brcms_b_*`. Hardware state changes happen in callees, especially clock, reset, interrupt, and memory operations.

Dependencies and integration: Includes `main.h`, `mac80211_if.h`, and `phy_shim.h`, and bridges PHY code to the main brcmsmac core and mac80211-facing private state. Risks: no null checking after attach, atomic allocation may fail, and type casts between `wlapi_timer` and `brcms_timer` rely on ABI equivalence. Test signals include PHY attach/detach error paths, timer lifecycle, interrupt mask restore, and register/SHM access under suspend/resume.
