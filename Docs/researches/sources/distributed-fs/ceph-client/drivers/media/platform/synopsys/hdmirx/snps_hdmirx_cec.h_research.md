# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx_cec.h

## Purpose
Declares the internal interface between the main Synopsys HDMI receiver driver and its CEC adapter implementation.

## Important APIs, Types, And Functions
`struct hdmirx_cec_ops` abstracts parent MMIO access and optional parent enable/disable hooks. `struct hdmirx_cec_data` is the registration input containing parent device, ops, Linux device, and IRQ. `struct hdmirx_cec` is the adapter runtime state. Exported functions are `snps_hdmirx_cec_register()` and `snps_hdmirx_cec_unregister()`.

## Control Flow
The main driver fills `hdmirx_cec_data` after obtaining the CEC IRQ and calls register during probe. Unregister is called during remove before main HDMI resources are fully disabled.

## State And Persistence
The header defines in-memory state fields for the CEC adapter, including address mask, adapter, RX message, TX completion state, IRQ, and parent pointers. No persistent state exists.

## Dependencies And Integration Points
Requires a forward declaration of `struct snps_hdmirx_dev` and relies on the CEC core type `struct cec_adapter` being visible to C users through included media headers in implementation contexts. It is private to the hdmirx module.

## Risks
Because MMIO access is callback-based, the parent must keep registers mapped and clocks/interrupts valid while CEC is active. The header exposes runtime fields directly to the CEC implementation, so locking and memory-barrier discipline must be maintained there rather than enforced by types.

## Test Signals
Compile tests ensure the main and CEC objects agree on this private ABI. Runtime tests are the same CEC registration, IRQ, and transmit/receive checks used for `snps_hdmirx_cec.c`.
