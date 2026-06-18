
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/Kconfig

## Purpose
`Kconfig` declares configuration options for legacy Intel 82586/82593/82596 Ethernet devices and gates them by architecture/platform support.

## Important APIs, Types, And Functions
- `NET_VENDOR_I825XX` is the vendor menu switch, defaulting to `y` when `NET_VENDOR_INTEL` is enabled.
- `ARM_ETHER1` builds Acorn Ether1 support for `ARM && ARCH_ACORN`.
- `BVME6000_NET` builds 82596 support for BVME6000.
- `LASI_82596` builds HP PA-RISC LASI 82596 support for `GSC`.
- `MVME16x_NET` builds 82596 support for Motorola MVME16x.
- `SNI_82596` builds SNI RM 82596 support for `SNI_RM`.
- `SUN3_82586` builds Sun3 onboard 82586 support for `SUN3`.

## Control Flow
There is no runtime control flow. Kconfig selection determines which driver objects the Makefile builds and which platform code can reference these drivers.

## State And Persistence Behavior
No runtime state. The file controls compile-time configuration.

## Dependencies And Integration Points
It integrates with the kernel networking driver menu and `drivers/net/ethernet/i825xx/Makefile`. Platform dependencies prevent compiling hardware-specific drivers on unsupported architectures.

## Risks And Edge Cases
Incorrect dependencies can cause build failures from architecture-specific headers or hide valid drivers. `NET_VENDOR_I825XX` being only a menu gate means disabling it skips all child prompts.

## Test Signals
Kconfig allmodconfig/allyesconfig on supported architectures and dependency resolution for unsupported architectures are the main validation signals.
