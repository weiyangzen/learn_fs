# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/Kconfig

## Purpose
This file defines Broadcom STB suspend/resume support configuration.

## Important APIs, Types, And Functions
The symbol is `BRCMSTB_PM`, a bool defaulting to yes when visible. It depends on `PM` and `BMIPS_GENERIC` and is enclosed by `if SOC_BRCMSTB`.

## Control Flow
When `SOC_BRCMSTB` is enabled, Kconfig exposes `BRCMSTB_PM` only on BMIPS systems with PM support. The brcmstb Makefile uses it to include the `pm/` directory.

## State, Persistence, And Dependencies
Configuration persists in `.config`. Dependencies ensure PM code is only built for supported BMIPS generic platforms.

## Integration Points
Controls Broadcom STB platform suspend/resume code under `drivers/soc/bcm/brcmstb/pm/`.

## Risks
Default-y platform PM support can change suspend/resume behavior broadly on eligible systems. ARM/ARM64 BRCMSTB builds do not see this option due to `BMIPS_GENERIC` dependency.

## Test Signals
Check BMIPS generic PM builds, suspend/resume smoke tests, and verify non-BMIPS BRCMSTB configs do not select this option.
