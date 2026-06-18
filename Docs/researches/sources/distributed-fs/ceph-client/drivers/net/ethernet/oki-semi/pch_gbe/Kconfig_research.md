# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/Kconfig

## Purpose
Defines the EG20T/ML7223/ML7831 PCH Gigabit Ethernet driver option.

## Important APIs, Types, And Functions
`PCH_GBE` is a tristate depending on PCI, `(MIPS_GENERIC || X86_32 || COMPILE_TEST)`, and `PTP_1588_CLOCK`. It selects `MII`, `PTP_1588_CLOCK_PCH`, and `NET_PTP_CLASSIFY`.

## Control Flow
Selecting the symbol builds the multi-object PCH GBE driver as built-in or module.

## State And Persistence
Configuration state only.

## Dependencies And Integration Points
PTP selections support hardware timestamp code; `MII` supports generic MII ioctl and ethtool helpers.

## Risks And Edge Cases
The hard PTP dependency prevents a non-PTP build variant. Architecture gating limits visibility, with `COMPILE_TEST` retaining broader build coverage.

## Test Signals
Kconfig should select MII/PTP helpers and compile under target arches or `COMPILE_TEST` with PTP enabled.
