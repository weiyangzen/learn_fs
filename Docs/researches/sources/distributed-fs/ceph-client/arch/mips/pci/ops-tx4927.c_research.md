# sources/distributed-fs/ceph-client/arch/mips/pci/ops-tx4927.c

## Purpose
Implements Toshiba TX4927/TX4938 PCI controller config ops, setup, diagnostics, and PCI error interrupt handling.

## Important APIs, Types, And Functions
Key APIs are `get_tx4927_pcicptr`, `tx4927_pcibios_setup`, `tx4927_pcic_setup`, `tx4927_report_pcic_status`, `tx4927_dump_pcic_settings`, and `tx4927_pcierr_interrupt`. It installs a private `tx4927_pci_ops` and optionally declares an SLC90E66 bridge quirk.

## Control Flow
Setup records controller-to-register mappings, assigns `pci_ops`, disables initiator spaces, configures GB-to-PCI and PCI-to-GB windows, endian swap flags, timeout options, interrupt/status masks, optional internal arbiter, and command bits. Config reads/writes derive the controller from `bus->sysdata`, program config address, access endian-correct data lanes, and check/clear master abort. Error interrupt handling reports status, clears errors, or panics depending on `txx9_pci_err_action`.

## State And Persistence
Persists controller mappings in static `pcicptrs` and boot options in `tx4927_pci_opts`. Hardware window, mask, status, and arbiter registers are programmed for the boot lifetime.

## Dependencies And Integration Points
Depends on TXX9 PCI globals/options, TX4927 register layout, MIPS IRQ APIs, and board setup code that calls `tx4927_pcic_setup`.

## Risks And Edge Cases
Window size/offset calculations, endian flags, abort handling, and interrupt action policy are hardware-critical. `pcicptrs` supports only two controllers. Boot option parsing silently ignores invalid values.

## Test Signals
TX4927/TX4938 boot, PCI config scanning, PCI error interrupt injection, endian build coverage, and boot options `trdyto=`, `retryto=`, `gbwc=` validate behavior.
