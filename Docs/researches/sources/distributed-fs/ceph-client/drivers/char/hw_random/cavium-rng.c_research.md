# sources/distributed-fs/ceph-client/drivers/char/hw_random/cavium-rng.c

## Purpose
This PCI PF driver enables Cavium ThunderX RNG hardware and creates one SR-IOV virtual function. The companion VF driver registers the hwrng provider and reads random data.

## Important APIs, Types, and Functions
- `struct cavium_rng_pf` stores the mapped control/status register.
- `cavium_rng_probe()` maps BAR0, writes `THUNDERX_RNM_RNG_EN | THUNDERX_RNM_ENT_EN`, and enables one VF with `pci_enable_sriov()`.
- `cavium_rng_remove()` disables SR-IOV and clears the control register.
- PCI ID table matches device `0xa018`.

## Control Flow
When the PF is probed, it maps control registers, enables RNG and entropy source bits, stores driver data, and requests one VF. If SR-IOV setup fails, it disables hardware again. Remove tears down the VF first, then disables RNG hardware.

## State and Persistence Behavior
Persistent state is one MMIO control bitfield and PCI SR-IOV VF enablement. State is tied to the PF device lifecycle and does not directly register with hwrng.

## Dependencies and Integration Points
It depends on PCI, SR-IOV support, Cavium PCI IDs, and the VF driver `cavium-rng-vf.c` for actual hwrng data access.

## Risks
If SR-IOV enable fails, no hwrng provider appears even though the PF exists. The driver enables exactly one VF, so multi-consumer scaling is not attempted. Hardware remains enabled until remove or probe failure cleanup.

## Test Signals
Test PF probe, BAR mapping failure, SR-IOV unavailable/failure cleanup, VF creation and companion driver binding, and remove disabling both VF and hardware.
