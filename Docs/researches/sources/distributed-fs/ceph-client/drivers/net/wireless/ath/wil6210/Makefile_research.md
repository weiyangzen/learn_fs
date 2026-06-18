# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/Makefile

## Purpose
`Makefile` defines the `wil6210` kernel module composition and conditional object inclusion for debugfs and tracing support.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_WIL6210) += wil6210.o` ties module build to the Kconfig symbol.
- `wil6210-y` lists core objects: main, netdev, cfg80211, PCI bus, WMI, interrupt, TX/RX, eDMA TX/RX, debug, reorder, firmware, PM, PMC, platform, ethtool, crash dump, and P2P support.
- `wil6210-$(CONFIG_WIL6210_DEBUGFS)` and `wil6210-$(CONFIG_WIL6210_TRACING)` conditionally add `debugfs.o` and `trace.o`.
- `CFLAGS_trace.o := -I$(src)` lets the tracing framework locate `trace.h`.

## Control Flow
No runtime control flow exists. Build selection determines which translation units and optional feature code are linked into the module.

## State and Persistence Behavior
The file affects build artifacts only. It does not define runtime state.

## Dependencies and Integration Points
It depends on Kbuild conventions and symbols from `Kconfig`. The object order reflects driver subsystem boundaries: cfg80211 registration, WMI firmware control, bus/interrupt plumbing, TX/RX datapath, PM, and diagnostics.

## Risks and Test Signals
Risks include missing an object when adding cross-file APIs or breaking trace include paths. Test signals are clean incremental and full kernel builds with tracing/debugfs enabled and disabled.
