# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/jazzsonic.c

Purpose: platform driver for the onboard National Semiconductor SONIC Ethernet controller on MIPS Jazz systems. It provides Jazz-specific register access, probing, IRQ hookup, descriptor allocation/freeing, and delegates core SONIC operations to included `sonic.h`/`sonic.c`.

Important functions: `jazz_sonic_probe`, `sonic_probe1`, `jazzsonic_open`, `jazzsonic_close`, and `jazz_sonic_device_remove`. `sonic_netdev_ops` wires open/stop/start_xmit/get_stats/set_rx_mode/tx_timeout/address ops to wrapper or core SONIC functions. Register access macros `SONIC_READ` and `SONIC_WRITE` use volatile 32-bit MMIO via `dev->base_addr`.

Control flow: platform probe gets the memory resource, allocates an Ethernet device with `struct sonic_local`, stores device/driver data, assigns base address and IRQ, then calls `sonic_probe1`. `sonic_probe1` reserves the memory region, verifies a known silicon revision, resets the controller, reads the MAC address from CAM registers, sets 32-bit DMA mode, allocates descriptors, installs netdev ops, clears tally counters, and returns. Registering the netdev completes probe. Open requests the IRQ then calls `sonic_open`; close calls `sonic_close` then frees the IRQ.

State and persistence: netdev private `struct sonic_local` holds descriptor DMA state and device pointer. Descriptor memory is coherent DMA and freed on probe failure/remove. Hardware tally counters are cleared during probe; runtime state is managed by core SONIC code.

Dependencies and integration: depends on MIPS Jazz headers, Jazz DMA APIs, platform device resources, generic netdev/ethernet helpers, and included SONIC core implementation.

Risks: `#include "sonic.c"` makes compile-time coupling unusual but common for older platform variants. Probe assumes known revision `0x04`; unsupported but compatible revisions will be rejected. Direct volatile MMIO macros rely on correct register spacing. Error paths must release memory region and coherent descriptors exactly once.

Test signals: MIPS Jazz platform boot/probe, invalid revision rejection, MAC read correctness, IRQ open/close, packet TX/RX through core SONIC, multicast list updates, tx timeout handling, module/platform removal, and probe failure cleanup.
