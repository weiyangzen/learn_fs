# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ptp.h

Purpose: declares the LAN743x PTP/GPIO interface shared with the rest of the LAN743x driver. It defines chip GPIO limits, event-channel/perout/extts counts, PTP flags, TX timestamp queue sizing, GPIO state, perout state, external timestamp state, and the main `struct lan743x_ptp` layout.

Important APIs and types: `struct lan743x_gpio` tracks GPIO register shadows plus used/output/PTP bitmaps behind `gpio_lock`. `struct lan743x_ptp_perout` records the event channel and GPIO pin allocated to a periodic output. `struct lan743x_extts` stores EXTTS flags and the last captured timestamp. `struct lan743x_ptp` owns `ptp_clock_info`, pin descriptors, PHC pointer, command lock, event-channel bitmap, perout/extts arrays, LED mux state, and the fixed TX timestamp SKB/timestamp queues. Public functions expose init/open/close, ISR, TX timestamp reservation and SKB enqueue, hwtstamp get/set, GPIO init, and latency update.

Control flow and integration: LAN743x main, TX, RX, and ethtool/netdev code include this header to coordinate timestamping. TX code calls request/unrequest and SKB timestamp functions; RX/netdev code calls hwtstamp get/set and latency update; interrupt code calls `lan743x_ptp_isr`; probe/open lifecycle calls init/open/close.

State and persistence: the header defines the in-memory ABI between `lan743x_ptp.c` and the rest of the LAN743x driver. The fixed queue length `LAN743X_PTP_NUMBER_OF_TX_TIMESTAMPS` limits outstanding hardware TX timestamp work. `PTP_FLAG_PTP_CLOCK_REGISTERED` and `PTP_FLAG_ISR_ENABLED` drive close-time cleanup. GPIO register shadows persist across pin reservations to prevent unrelated pins from being overwritten.

Dependencies and integration points: depends on Linux PTP clock and netdevice types plus `struct lan743x_adapter` from the main driver. Constants reflect LAN7430/LAN7431/PCI11x1x hardware limits, including LAN7430 LED-multiplexed GPIOs and eight PCI11x1x PTP-IO channels.

Risks and test signals: layout changes can break timestamp queue management, close-time cleanup, or users of the exported functions. Compile coverage should include LAN743x TX/RX/main users and both PTP-enabled and PTP-disabled builds. Runtime tests should validate the fixed queue limit, GPIO reservation/release, and PHC registration flags through repeated open/close cycles.
