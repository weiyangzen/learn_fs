<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/kempld_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/kempld_wdt.c`

Purpose: Kontron PLD watchdog driver for a staged hardware watchdog where the hardware pretimeout stage runs before the final timeout stage, opposite to the kernel API view.

Important APIs, types, and functions: `struct kempld_wdt_data` stores PLD parent data, watchdog core device, stage descriptors, pretimeout, and PM status. Stage helpers set action, timeout, and read programmed timeout using PLD clock and prescaler. `kempld_wdt_probe_stages()` discovers writable stage byte masks and assigns timeout/pretimeout stages. `kempld_wdt_ioctl()` implements legacy pretimeout ioctls.

Control flow: probe reads PLD config and forces nowayout if enable/global lock bits are set, attaches watchdog core, discovers stages, programs module timeout/pretimeout, imports existing hardware settings if enabled, installs stop-on-reboot/unregister, and registers. Start programs timeout action then sets enable. Stop clears enable and verifies it. Ping writes `'K'` to kick register. Suspend stores config and stops if enabled; resume restores active/stopped state.

State and persistence: watchdog state persists in PLD registers, including lock bits that can make nowayout mandatory. Timeout and pretimeout are reconstructed from stage registers when firmware left the watchdog enabled. Hardware stages are described by masks discovered at runtime.

Dependencies and integration points: depends on the parent `kempld` MFD, PLD mutex/register APIs, PLD clock rate, optional NMI feature mask, watchdog core, platform PM hooks, and module parameters.

Risks and test signals: risks include stage assignment bugs, inverted pretimeout semantics, lock-bit handling, prescaler rounding, and ioctl/core pretimeout inconsistencies. Test stage probing on one- and two-stage PLDs, locked watchdogs, pretimeout NMI delivery, suspend/resume with BIOS-modified state, and timeout reconstruction from existing registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/kempld_wdt.c -->
