# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.h

## Purpose

`qlcnic_hw.h` is the public hardware-command interface for the qlcnic driver. It defines shared register indexes, access macros, firmware mailbox command IDs, mailbox/event constants, ring limits, and function prototypes for 82xx hardware operations and common helper entry points used by the rest of the driver.

## Important APIs, Types, And Constants

- `enum qlcnic_regs` defines indexes into `ahw->reg_tbl` for PEG halt status, heartbeat, firmware capabilities, driver/device state, driver scratch, NPAR state, firmware versions, API version, and flash locking.
- `QLC_SHARED_REG_RD32()` and `QLC_SHARED_REG_WR32()` access BAR0 offsets through the shared register table.
- `QLCRDX()` and `QLCWRX()` access family-specific extended register tables.
- `QLCNIC_CMD_*` constants enumerate firmware mailbox commands for contexts, MAC/VLAN, PCI/NIC info, eSwitch, DCB, statistics, interrupts, RSS, LED, link, NIC init/stop, driver version, and encapsulation.
- Interrupt, MAC operation, and mailbox event constants define firmware protocol values.
- `struct qlcnic_mailbox_metadata` records mailbox command ID and argument counts.
- Mailbox ownership/response constants (`QLCNIC_GET_OWNER`, `QLCNIC_MBX_TIMEOUT`, `QLCNIC_MBX_RSP_OK`, `QLCNIC_MBX_ASYNC_EVENT`) support mailbox synchronization.
- Ring limits define maximum hardware TX, vNIC TX, driver TX, and SDS ring counts.
- Function prototypes expose 82xx register access, NAPI, promisc/MAC filter, coalescing, RSS, LRO, IP notification, link event, loopback, CRB access, mailbox, context, board/LED, function, API lock, shutdown/resume, and firmware dump helpers.

## Control Flow Role

This header enables the driver's function-table style. `qlcnic_main.c` assigns concrete 82xx functions declared here into `struct qlcnic_hardware_ops` and `struct qlcnic_nic_template`; higher-level code then calls generic wrappers. Register macros turn enum indexes into BAR0 offsets after family-specific register tables have been installed.

Mailbox command constants flow into command allocation and issue paths: callers choose a `QLCNIC_CMD_*`, allocate command args, populate input values, and invoke the hardware mailbox operation.

## State And Persistence Behavior

The header has no mutable runtime state, but it names persistent firmware and hardware state: driver active masks, device state, reset/quiesce acknowledgements, firmware versions, API level, NPAR state, and flash lock ownership. These values are used across probe, reset, power management, AER, and health polling.

## Dependencies And Integration Points

It depends on qlcnic structures declared elsewhere and Linux types such as `struct net_device`, `struct pci_dev`, `struct ethtool_coalesce`, and `netdev_features_t`. It is included by `qlcnic_hw.c`, `qlcnic_init.c`, `qlcnic_main.c`, and related driver files.

## Risks

- Register macros do no bounds checking, so wrong enum values or mismatched tables can cause invalid MMIO.
- Command IDs are firmware ABI values; using the wrong constant may compile but misconfigure firmware.
- Many declarations are 82xx-specific and must be called through chip checks or operation tables.
- Ring-limit constants must remain synchronized with firmware context and MSI-X vector assumptions.

## Test Signals

Build coverage catches declaration/definition drift. Runtime coverage comes from probe shared-register access, mailbox command execution, MSI-X/ring sizing, RSS/LRO/LED/link/MAC/VLAN operations, and absence of invalid MMIO during reset and firmware transitions.
