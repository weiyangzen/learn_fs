# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec.h

### Purpose
`fec.h` is the shared private header for the main NXP/Freescale Fast Ethernet Controller driver (`fec_main.c`) and its PTP companion (`fec_ptp.c`). It defines register offsets for multiple FEC register layouts, descriptor formats, interrupt/status bits, queue sizing, SoC quirk flags, per-queue state, the main private device state, and the PTP function contract.

### Important APIs, Types, And Functions
The file defines two register offset sets: the common FEC/ENET layout and the `CONFIG_M5272` ColdFire layout. It abstracts descriptor endianness with `fec16_to_cpu`, `fec32_to_cpu`, `cpu_to_fec16`, and `cpu_to_fec32`, because ARM/ARM64 FEC blocks use little-endian descriptors while other platforms use big-endian ordering. `struct bufdesc` is the basic RX/TX descriptor, and `struct bufdesc_ex` adds enhanced fields for checksum, VLAN, AVB queue, and timestamp support.

Important state types are `struct bufdesc_prop`, `struct fec_enet_priv_tx_q`, `struct fec_enet_priv_rx_q`, `union fec_rx_buffer`, `struct fec_tx_buffer`, `enum fec_txbuf_type`, `struct fec_stop_mode_gpr`, and `struct fec_enet_private`. `fec_enet_private` owns MMIO base, clocks, queue arrays, platform and PHY/MDIO data, IRQs, quirk flags, NAPI, work items, PTP clock/timecounter fields, interrupt coalescing settings, stop-mode state, XDP program pointer, AF_XDP pools via queues, and flexible ethtool stats storage. The exported internal PTP declarations are `fec_ptp_init()`, `fec_ptp_stop()`, `fec_ptp_start_cyclecounter()`, `fec_ptp_save_state()`, `fec_ptp_restore_state()`, `fec_ptp_set()`, and `fec_ptp_get()`.

### Control Flow
The header has no runtime control flow but strongly shapes it. `fec_main.c` uses descriptor and ring metadata to allocate queues, start hardware, transmit SKBs/TSO/XDP frames, receive into page pools or XSK buffers, and clean descriptors. PTP flow is enabled when `FEC_QUIRK_HAS_BUFDESC_EX` and a PTP clock are available, with enhanced descriptors carrying timestamps. Quirk bits gate large areas of driver behavior: ENET-MAC mode, frame byte swapping, gasket setup, gigabit support, enhanced descriptors, checksum/VLAN offloads, AVB multi-queue support, hardware erratum workarounds, RACC, coalescing, EEE, wakeup, MDIO Clause 45, and jumbo frames.

### State, Persistence, And Dependencies
Runtime state is entirely in kernel memory and hardware registers. It is not persisted across reboot, but the driver may save and restore PTP time state across MAC reset using `ptp_saved_state`. Dependencies include Linux BPF/XDP, page pool, PTP clock/timecounter, phylib, PM QoS, i.MX SCU firmware, and dt-bindings for i.MX resources.

### Integration Points
The header is the compile-time integration point between the main netdev implementation and PTP implementation. It also maps hardware details into Linux networking subsystems: netdev features, XDP memory models, page pools, MDIO/PHY, runtime PM, and ethtool stats.

### Risks
Descriptor layout and endian selection are high risk because they affect DMA ownership. Several constants are power-of-two or alignment-sensitive (`TX_RING_SIZE`, `TX_RING_MOD_MASK`, XDP headroom, descriptor size log2). Quirk combinations must match actual SoC integration; a wrong quirk can enable unsupported registers or omit required errata handling. `struct fec_enet_private` is a shared contract, so field changes can break PTP, PM, XDP, and queue logic together.

### Test Signals
Build coverage should include ARM/ARM64, ColdFire/M5272, COMPILE_TEST, PTP-enabled and PTP-disabled variants. Runtime signals include descriptor wrap handling, multi-queue AVB routing, checksum/VLAN offloads, XDP/AF_XDP paths, PTP timestamp availability, suspend/resume with WOL, and jumbo MTU configuration on quirked hardware.
