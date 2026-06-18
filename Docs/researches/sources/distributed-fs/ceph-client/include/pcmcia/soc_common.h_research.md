# sources/distributed-fs/ceph-client/include/pcmcia/soc_common.h

Purpose: declares the shared SoC PCMCIA socket adapter layer used by platform-specific low-level drivers. It embeds a generic `pcmcia_socket` and adds GPIO, regulator, clock, resource, timing, polling, and CPU-frequency state needed by non-PCI SoC controllers.

Important APIs and types: `struct pcmcia_state` captures card-detect, ready, battery/status, write-protect, and voltage-sense bits returned by low-level hardware. `struct soc_pcmcia_regulator` tracks regulator object and on/off state. `struct soc_pcmcia_socket` owns the generic socket, socket index, clock, low-level ops pointer, cached socket status/config state, I/O/memory/attribute timing arrays, resource ranges, six status GPIO/IRQ slots (`SOC_STAT_CD`, `BVD1`, `BVD2`, `RDY`, `VS1`, `VS2`), reset/bus-enable GPIOs, Vcc/Vpp regulators, optional CPUFreq notifier, poll timer, list node, and private driver data. `struct pcmcia_low_level` is the hardware callback table for init/shutdown, state sampling, socket configuration, interrupt enable/disable, timing calculation/programming/reporting, and optional frequency-change handling.

Control flow: platform code provides `pcmcia_low_level`, initializes each `soc_pcmcia_socket`, and lets common SoC code translate GPIO/state changes into generic PCMCIA socket events. Hardware init configures resources, clocks, GPIOs, IRQ/polling, and regulators; `configure_socket()` applies Vcc/Vpp/reset/output state; suspend disables status IRQs and the bus; resume or reinitialization restores status handling and timing.

State and persistence: state is per-socket kernel runtime state. Regulator `on` flags, cached `cs_state`, speed arrays, status bits, IRQ state, and resources persist only for the device lifetime and across suspend/resume while the driver remains loaded. No card data is persisted.

Dependencies and integration points: depends on `pcmcia/ss.h`, clocks, regulators, GPIO descriptors, timers, resources, optional CPUFreq notifiers, and module ownership. It bridges SoC-specific board code with generic PCMCIA socket registration and event parsing.

Risks and test signals: risks include GPIO polarity/index mistakes, regulator state desynchronization, timing not updated after CPU frequency changes, poll timer races during shutdown, and mismatched resource windows. Test by probing/removing SoC sockets, card insert/remove events via GPIO IRQ and polling, Vcc/Vpp transitions, suspend/resume, CPUFreq transition timing, and status-bit mapping for memory and I/O cards.
