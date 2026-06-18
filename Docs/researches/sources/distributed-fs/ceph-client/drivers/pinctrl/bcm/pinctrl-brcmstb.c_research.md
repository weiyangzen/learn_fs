<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.c

## Purpose
This is the shared pinctrl implementation for Broadcom STB-style pin controllers used by BCM2712 data in this subset. It registers pinctrl, pinmux, and generic bias pinconf operations, with one pin per group and per-pin function tables supplied as match data.

## Important APIs, Types, And Functions
`struct brcmstb_pinctrl` stores MMIO base, copied descriptor, pin register metadata, per-pin function mappings, function names, GPIO group names, GPIO range, and a spinlock. `brcmstb_pinctrl_fsel_get()` reads a pin's mux field and maps hardware fsel to logical function ID. `brcmstb_pinctrl_fsel_set()` maps a logical function back to an fsel value and writes the mux bits. `brcmstb_pull_config_get()` and `brcmstb_pull_config_set()` read/write two-bit pad pull fields. `brcmstb_pinctrl_probe()` is exported for SoC data files.

## Control Flow
Probe gets match data, maps MMIO, copies the SoC descriptor, installs common pctl/pmx/pinconf ops, builds a list of one-pin group names from pin descriptors, stores SoC register/function tables, registers pinctrl, and adds the GPIO range. Runtime mux selection calls `brcmstb_pmx_set()`, which validates the group, resolves the pin descriptor number, and writes fsel. GPIO request/free paths set the pin back to the SoC's GPIO function. Pinconf generic bias operations read and write pad bits when a pad bit exists.

## State And Persistence
Runtime software state is the `brcmstb_pinctrl` object and generated group-name array. Hardware persists mux and pull state. The core does not manage GPIO data or interrupts; it only exposes mux and bias control. Pins without mux bits, such as eMMC-only pads, cannot be muxed but may still have pull configuration.

## Dependencies And Integration Points
Depends on OF match data supplied by a SoC-specific file, Linux pinctrl/pinmux/pinconf-generic, MMIO helpers, and `pinctrl-brcmstb.h`. It exports `brcmstb_pinctrl_probe()` to module users.

## Risks
Function mapping is subtle because callers can pass either logical function IDs or fsel-like values; invalid function IDs return `-EINVAL`. Debug messages index `func_names` with current fsel in some paths, so table consistency matters. Bias writes share the same spinlock as mux writes, protecting MMIO read/modify/write but coupling unrelated register domains.

## Test Signals
Use pinctrl debugfs to inspect group names, function names, and pin states. Apply mux and bias states for pins with and without mux bits. Confirm GPIO requests return pins to GPIO function and that invalid functions or pads without pull bits fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.c -->
