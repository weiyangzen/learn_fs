# sources/distributed-fs/ceph-client/include/linux/firmware/imx/sci.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/sci.h` aggregates i.MX System Controller Interface service headers and declares SCU IRQ/SOC initialization helpers. The source was read as a complete 57-line file for this report.

## Important APIs, Types, and Functions

It includes SCU IPC plus MISC, PM, and RM service headers. APIs include `imx_scu_enable_general_irq_channel`, notifier register/unregister, `imx_scu_irq_group_enable`, `imx_scu_irq_get_status`, and `imx_scu_soc_init`, with `-EOPNOTSUPP` stubs when `CONFIG_IMX_SCU` is disabled.

## Control Flow

Platform code initializes SCU SOC support, enables a general IRQ channel, registers notifiers, enables IRQ groups, and queries group status through firmware-backed calls.

## State and Persistence Behavior

No state is owned here. IRQ channels, notifier lists, and SOC data are owned by the SCU implementation and firmware.

## Dependencies and Integration Points

It integrates with i.MX SCU firmware, notifier chains, IRQ service groups, SOC initialization, and included PM/RM/MISC services.

## Risks and Edge Cases

The mutual includes between `sci.h` and service headers rely on include guards. Disabled stubs uniformly return unsupported, so clients must handle absent SCU hardware.

## Test Signals

SCU IRQ notifier tests, group enable/status tests, SOC init tests, and disabled-config build coverage.
