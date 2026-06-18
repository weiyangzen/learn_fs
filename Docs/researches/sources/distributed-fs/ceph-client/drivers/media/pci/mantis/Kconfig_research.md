# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/Kconfig

## Purpose
This Kconfig file defines build-time options for the Mantis/Hopper PCI bridge DVB drivers.

## Important APIs, Types, and Functions
It defines `MANTIS_CORE`, `DVB_MANTIS`, and `DVB_HOPPER`. The card options select frontend/tuner dependencies such as MB86A16, ZL10353, STV0299, LNBP21, STB0899, STB6100, TDA665x, TDA10021, TDA10023, and DVB_PLL when media subdriver autoselection is enabled.

## Control Flow
There is no runtime control flow. Kconfig dependency resolution controls which modules can be built and which helper frontend drivers are selected.

## State and Persistence Behavior
No runtime state is stored. The selected symbols persist in the kernel build configuration and determine object inclusion.

## Dependencies and Integration Points
All options require PCI, I2C, DVB core support, and the core bridge. `MANTIS_CORE` also depends on INPUT and RC_CORE. The symbols feed the local Makefile's `obj-$(CONFIG_...)` rules.

## Risks
Missing `select` dependencies can produce a driver that probes but lacks its frontend. Over-selection can pull unnecessary modules into builds. The help text and dependencies must match actual card support.

## Test Signals
Build matrix coverage for disabled core, core-only, DVB_MANTIS, DVB_HOPPER, built-in vs module, and MEDIA_SUBDRV_AUTOSELECT on/off catches configuration issues.
