# Research: subset-b-005905

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_commands.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_commands.h

## Purpose
This header is the Linux copy of the ChromeOS Embedded Controller host-command ABI. It is explicitly auto-generated from the ChromiumOS EC `ec_commands.h` source and defines the constants, packet layouts, command ids, request/response payload structures, bit masks, and persistent host-visible data maps used by ChromeOS EC transport drivers and client drivers. It is not Ceph-specific; in this source tree it is kernel platform data used by the ChromeOS EC stack.

## Important APIs, Types, And Constants
The file starts with protocol and transport constants: `EC_PROTO_VERSION`, LPC/ACPI I/O addresses, LPC status bits, EC memory-map offsets, temperature/fan/battery/switch encodings, and ACPI memory locations. It defines alignment annotations such as `__ec_align4` and the core packet structs `ec_lpc_host_args`, `ec_host_request`, `ec_host_response`, `ec_host_request4`, and `ec_host_response4`. `enum ec_status` is the command-result namespace, while `enum host_event_code` plus `EC_HOST_EVENT_MASK()` define stable host event ids.

The command table covers general probing (`EC_CMD_HELLO`, `EC_CMD_GET_VERSION`, `EC_CMD_GET_FEATURES`), flash and vboot commands, PWM/lightbar/LED commands, motion sense, MKBP event delivery, thermal, host event masks, GPIO and I2C passthrough, charging and battery state, sleep/hibernate, CEC/audio codec/WoV, reboot/panic, USB-PD and Type-C, regulators, peripheral charging, UCSI PPM, fingerprint, touchpad, EC-to-EC battery/charger, board-specific ranges, and passthrough command routing. Many commands are versioned with separate v0/v1/v2 payload structs and feature bits.

## Control Flow And State
The file has no executable code, but it documents several protocol state machines. ACPI read/write commands require ordered writes and waits on LPC status bits. Protocol v3 uses request/response checksums and length headers. Protocol v4 adds sequence numbers, duplicate retry semantics, header CRC, optional data CRC, and explicit host/EC algorithms. Persistent or stateful EC domains include flash protection and regions, VBNV/PSTORE/VSTORE storage, RTC/alarm, host event masks, wake masks, hibernate timers, sleep transition timeout accounting, sensor FIFO state, battery sustainer thresholds, Type-C event queues, fingerprint templates/context/encryption seed, and passthrough sub-device routing.

## Dependencies And Integration Points
This header depends on `linux/bits.h` and `linux/types.h`; many downstream declarations are consumed by `cros_ec_proto.h`, ChromeOS EC MFD/transport drivers, IIO sensorhub, power supply, Type-C/PD, input, hwmon, charger, fingerprint, touchpad, and userspace-facing debug or char devices. The ABI must match EC firmware exactly, including struct packing, flexible array payloads, command versions, and value ranges. The source comments also show integration with ACPI, LPC, I2C, SPI, ISH, PD MCU passthrough, and board-specific command reservations.

## Risks And Test Signals
Primary risk is ABI drift: changing field order, packing, command values, enum values, bit positions, or max sizes can break firmware communication. Version negotiation must use `EC_CMD_GET_CMD_VERSIONS`, `EC_CMD_GET_PROTOCOL_INFO`, and feature masks before assuming payload layouts. Several commands are deprecated or write-protect gated, and some are security-sensitive: flash writes, I2C passthrough, fingerprint templates, battery firmware update, vboot storage, and host event wake masks. Test signals include successful hello/version/protocol probes, checksum/CRC failure tests, feature-bit gating, MKBP event decoding across v0/v1/v3 response sizes, motion FIFO overflow handling, Type-C status/event round trips, and fingerprint/template boundary reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_proto.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_proto.h

## Purpose
This header defines the Linux-side protocol interface for ChromeOS EC devices. It wraps the raw command ABI from `cros_ec_commands.h` in kernel device structures, transport hooks, platform naming, transfer helpers, event notifiers, and command buffer metadata used by ChromeOS EC MFD children and transport drivers.

## Important APIs And Types
The core request object is `struct cros_ec_command`, with command version, command id, outgoing size, maximum incoming size, result code, and flexible payload buffer. `struct cros_ec_device` is the transport/device state: physical name, device/class pointers, optional memory-map reader, size limits, private transport data, IRQ, aligned input/output buffers, wake/suspend/registration flags, `cmd_xfer` and `pkt_xfer` transport callbacks, mutex serialization, MKBP support, host sleep metadata, event and panic notifier heads, and child platform devices for main EC and PD. `struct cros_ec_platform` carries MFD platform naming and command offset, while `struct cros_ec_dev` is the class-facing EC device wrapper with debugfs, feature cache, and command offset. Exported helpers include `cros_ec_prepare_tx()`, `cros_ec_check_result()`, `cros_ec_cmd_xfer()`, and `cros_ec_cmd_xfer_status()`.

## Control Flow, State, And Persistence
The header describes synchronous command flow: callers populate `cros_ec_command`, transport code prepares protocol bytes, sends with `cmd_xfer` or `pkt_xfer`, then checks EC result separately from bus errors. The device mutex enforces one transaction at a time. Persistent runtime state includes probed protocol version, max request/response/passthrough sizes, wake state, suspend state, cached feature bits, last host sleep result, host event wake mask, MKBP event payload, and event timestamps.

## Dependencies And Integration Points
It includes Linux device, mutex, lockdep, notifier, and ChromeOS EC command ABI headers. It is the shared contract among EC physical transports such as LPC/I2C/SPI/ISH, the MFD core, EC char/debug interfaces, PD child devices, MKBP input/event handling, suspend/resume code, and panic notification consumers.

## Risks And Test Signals
The main risks are buffer sizing against transport overhead, unaligned payload handling, command result confusion with transport errors, notifier ordering during suspend/resume, and stale cached protocol limits after EC reboot. Test signals include successful feature probing, command transfer under each transport, command-status helper behavior for non-success EC results, MKBP event notifier delivery, wake mask behavior across suspend, and EC reboot/interface-ready re-query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_sensorhub.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_sensorhub.h

## Purpose
This header describes the ChromeOS EC MEMS sensor hub platform interface. It connects EC motion-sense FIFO commands to Linux IIO sensor devices, timestamp correction, batching, overflow handling, and push callbacks.

## Important APIs And Types
`struct cros_ec_sensor_platform` maps an IIO sensor child to an EC sensor id. `cros_ec_sensorhub_push_data_cb_t` is the per-sensor callback used to push a 3-axis sample and AP-domain timestamp into an IIO device. `struct cros_ec_sensors_ring_sample` stores packed FIFO samples. Timestamp state is split into EC overflow state, median filter history (`cros_ec_sensors_ts_filter_state`), and per-sensor batch state (`cros_ec_sensors_ts_batch_state`). `struct cros_ec_sensorhub` aggregates the EC device, reusable `cros_ec_command`, motion-sense params/response pointers, command mutex, MKBP notifier, FIFO ring, timestamp slots, FIFO info, overflow/filter state, future timestamp statistics, and per-sensor push callback table. Public functions register/unregister push callbacks, allocate/add/remove the ring, and enable FIFO interrupts.

## Control Flow, State, And Persistence
Sensorhub control flow is event-driven: EC MKBP/FIFO notifications trigger FIFO reads through the shared command buffer; ring samples are timestamp-corrected, batched, and dispatched to registered IIO callbacks. The state is runtime-only and maintained in memory: timestamp filter history, overflow offsets, batch metadata, FIFO sizing, and future timestamp clamp statistics. No disk persistence exists.

## Dependencies And Integration Points
The header depends on `ktime`, mutexes, notifiers, ChromeOS EC motion-sense ABI, and IIO forward declarations. Integration points are the ChromeOS EC core notifier chain, IIO sensor drivers, motion sense commands in `cros_ec_commands.h`, and power-management paths that enable/disable FIFO interrupts.

## Risks And Test Signals
Risks concentrate around timestamp correctness, EC counter overflow, FIFO overflow/loss accounting, concurrent command-buffer access, unregistering callbacks while events are in flight, and future timestamps that must be clamped. Test signals include FIFO enable/disable round trips, ring allocation bounds, per-sensor callback registration, batched sample ordering, overflow repair tests, median timestamp filter behavior under jitter, and IIO sample timestamps staying monotonic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_sensorhub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_usbpd_notify.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/cros_usbpd_notify.h

## Purpose
This small header exposes the ChromeOS USB Power Delivery notification registration API. It lets kernel consumers subscribe to USB-PD events through a notifier block without depending on a concrete driver internals header.

## Important APIs And Types
The public API is `cros_usbpd_register_notify(struct notifier_block *nb)` and `cros_usbpd_unregister_notify(struct notifier_block *nb)`. The only type dependency is Linux `struct notifier_block`.

## Control Flow, State, And Persistence
The header declares notifier registration only; the state lives in the provider driver's notifier chain. Registered callbacks are called when the USB-PD provider emits events, and unregister removes the callback from that chain. No persistent state or storage is described here.

## Dependencies And Integration Points
It depends on `linux/notifier.h` and integrates ChromeOS PD notification producers with consumers such as Type-C, power-supply, charger, or policy drivers.

## Risks And Test Signals
Risks are normal notifier-chain risks: unregister must happen before callback storage disappears, callbacks must tolerate provider teardown, and event meanings must match provider documentation. Test signals include successful registration/unregistration, event callback delivery, module unload without use-after-free, and behavior when no notifier provider is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/cros_usbpd_notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/crypto-ux500.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/crypto-ux500.h

## Purpose
This header defines platform data for ST-Ericsson UX500 crypto/hash hardware. It supplies DMA channel configuration and filter hooks used by the UX500 crypto drivers.

## Important APIs And Types
`struct hash_platform_data` carries a `mem_to_engine` filter parameter and a `dma_filter()` callback that selects a `dma_chan`. `struct cryp_platform_data` contains two `stedma40_chan_cfg` objects for memory-to-engine and engine-to-memory DMA directions.

## Control Flow, State, And Persistence
There is no executable control flow. Board or platform code fills these structures before driver probe. The crypto driver consumes them while requesting DMA channels and configuring transfer direction. State is static platform configuration and is not persisted by this header.

## Dependencies And Integration Points
It depends on the DMAengine API and `dma-ste-dma40.h`. It integrates UX500 crypto/hash drivers with the ST-Ericsson DMA40 controller and board-specific DMA request routing.

## Risks And Test Signals
Incorrect DMA filter parameters or channel configs can make crypto transfers hang, corrupt buffers, or silently fall back incorrectly. Test signals include successful DMA channel request, hash/cryp throughput tests, bidirectional DMA transfer completion, and probe deferral behavior when DMA resources are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/crypto-ux500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/davinci-cpufreq.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/davinci-cpufreq.h

## Purpose
This header defines TI DaVinci CPU frequency platform support data and the init entry point for the DaVinci cpufreq driver.

## Important APIs And Types
`struct davinci_cpufreq_config` provides a `cpufreq_frequency_table`, optional voltage-setting callback indexed by frequency-table entry, and optional platform init callback. `davinci_cpufreq_init()` is declared when `CONFIG_CPU_FREQ` is enabled and becomes a no-op inline otherwise.

## Control Flow, State, And Persistence
Platform code supplies frequency and voltage policy. The cpufreq driver calls initialization, selects operating points, and uses `set_voltage()` before or during frequency changes according to driver policy. State is runtime CPU frequency/voltage configuration; this header stores no persistent data.

## Dependencies And Integration Points
It depends on the generic Linux cpufreq table API and integrates DaVinci board setup with the cpufreq core and regulator/voltage code behind the callback.

## Risks And Test Signals
Risks include voltage/frequency mismatch, missing init on platforms requiring setup, and invalid frequency tables. Test signals include cpufreq policy registration, available frequency list correctness, transition tests under load, voltage callback ordering, and no-op behavior when CPU_FREQ is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/davinci-cpufreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/davinci_asp.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/davinci_asp.h

## Purpose
This header describes TI DaVinci McASP audio serial port platform data. It feeds board-specific DMA offsets, SRAM use, serializer layout, TDM slot counts, and clocking modes into the McASP audio driver.

## Important APIs And Types
`struct davinci_mcasp_pdata` includes TX/RX DMA offsets, EDMA event queues, SRAM playback/capture sizes and pool, channel-combine mode, `i2s_accurate_sck`, TDM slot counts, operation mode, serializer count and directions, hardware version, DMA event watermarks, and explicit TX/RX DMA channels. Constants enumerate McASP hardware versions, inactive/TX/RX serializer modes, and IIS/DIT operation modes. `snd_platform_data` aliases this structure for legacy users.

## Control Flow, State, And Persistence
The header has no executable control flow. During probe, the audio driver reads this data to configure serializers, DMA channels, SRAM buffering, and bit-clock behavior. State is board/static hardware description plus runtime audio stream configuration derived from it.

## Dependencies And Integration Points
It depends on `linux/genalloc.h` for SRAM pools and integrates with ALSA SoC, EDMA, DaVinci/OMAP platform code, and board wiring that decides serializer direction and clocking.

## Risks And Test Signals
Risks include left/right channel swaps when channel combine changes behavior, underruns if DMA queues or event thresholds are wrong, incorrect serializer direction, and clock accuracy problems with asymmetric frame sync. Test signals include playback/capture on all serializers, TDM slot mapping, underrun recovery, DMA channel allocation, and I2S bit-clock/frame-sync measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/davinci_asp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-dw.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-dw.h

## Purpose
This header provides platform data for Synopsys DesignWare DMA controllers and their slave devices. It describes controller capacity, channel allocation policy, bus master widths, burst limits, handshake polarity, and quirks.

## Important APIs And Types
`struct dw_dma_slave` describes a slave endpoint: DMA master device, source/destination request lines, memory/peripheral bus masters, permitted channel mask, and handshake polarity. `struct dw_dma_platform_data` describes the controller: number of masters/channels, allocation and priority order, max block size, per-master data widths, per-channel multi-block and max-burst support, protection-control bits, and quirk flags such as `DW_DMA_QUIRK_XBAR_PRESENT`. Constants cap masters/channels and define burst and protection masks.

## Control Flow, State, And Persistence
There is no code flow here. Platform data is consumed at controller and slave probe to restrict channel selection and program hardware descriptors. State is static hardware topology and controller capability.

## Dependencies And Integration Points
It depends on Linux bits/types and forward-declares `struct device`. It integrates the DesignWare DMA engine driver with platform devices, DMAengine slave configuration, and possible crossbar routing.

## Risks And Test Signals
Incorrect request ids, channel masks, bus master assignment, burst limits, or data widths can cause failed channel allocation or broken transfers. Test signals include DMAengine channel requests from each slave, memory-to-device and device-to-memory transfers, burst-size validation, multi-block operation, and behavior with crossbar-present platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-dw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-hsu.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-hsu.h

## Purpose
This header defines platform slave data for Intel High Speed UART DMA. It maps a consumer to a specific HSU DMA controller device and channel id.

## Important APIs And Types
`struct hsu_dma_slave` contains `dma_dev`, the DMA master device, and `chan_id`, the channel identifier to request or match.

## Control Flow, State, And Persistence
No executable control flow is defined. UART or serial platform code supplies this structure, and the DMA engine driver or filter uses it during channel selection. The state is static platform routing.

## Dependencies And Integration Points
It forward-declares `struct device` and integrates serial/HSUART clients with the HSU DMA controller through platform data.

## Risks And Test Signals
Wrong channel ids or device pointers lead to failed DMA channel lookup or data routed through the wrong channel. Test signals include UART TX/RX DMA operation, fallback to PIO if supported, suspend/resume with DMA active, and channel allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-hsu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-iop32x.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-iop32x.h

## Purpose
This header defines Intel IOP32x/IOP ADMA data structures shared by platform code and the ADMA DMAengine driver. It covers hardware ids, descriptor slot management, DMAengine embedding, and async transaction metadata.

## Important APIs And Types
Constants define descriptor slot size, threshold, paranoia checks, and hardware ids `DMA0_ID`, `DMA1_ID`, and `AAU_ID`. `struct iop_adma_device` wraps a platform device, hardware selector, descriptor pool DMA/CPU addresses, and embedded `dma_device`. `struct iop_adma_chan` tracks pending operations, spinlock, MMIO base, descriptor chain, parent device, embedded `dma_chan`, slot allocation lists, and IRQ tasklet. `struct iop_adma_desc_slot` represents software descriptors with list nodes, hardware descriptor pointer, transaction grouping, async_tx descriptor, and result pointers for XOR/CRC/PQ checks. `struct iop_adma_platform_data` supplies hardware id, capabilities, and descriptor pool size.

## Control Flow, State, And Persistence
The runtime model is descriptor-slot based: channels allocate slots from `all_slots`, chain operations, batch pending hardware submissions, and clean up from a tasklet after interrupts. The header stores no persistence; all state is in memory.

## Dependencies And Integration Points
It depends on Linux types, DMAengine, interrupts/tasklets, platform devices, lists, and async_tx consumers. Integration points are RAID/XOR/CRC/PQ acceleration and DMAengine clients on Intel IOP platforms.

## Risks And Test Signals
Risks include descriptor pool sizing, slot leaks, incorrect grouping for multi-slot transactions, races on `lock`, and misuse of hardware descriptor pointer macros. Test signals include memcpy/XOR/CRC/PQ DMAengine capability tests, interrupt cleanup, transaction dependency ordering, pool exhaustion, and DEBUG paranoia assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-iop32x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-mcf-edma.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-mcf-edma.h

## Purpose
This header defines ColdFire/Freescale eDMA platform data. It connects platform DMA channel counts and slave maps to the eDMA engine driver.

## Important APIs And Types
It declares `mcf_edma_filter_fn(struct dma_chan *chan, void *param)` and the helper macro `MCF_EDMA_FILTER_PARAM(ch)`. `struct mcf_edma_platform_data` contains the number of DMA channels, a pointer to a `dma_slave_map`, and the number of slave-map entries.

## Control Flow, State, And Persistence
No executable control flow is implemented here. Platform setup provides channel counts and slave mappings; DMA consumers use the filter parameter to match specific channels. State is static hardware routing.

## Dependencies And Integration Points
The header forward-declares `struct dma_slave_map` and uses `struct dma_chan`. It integrates ColdFire platform code, DMAengine slave maps, and eDMA consumer drivers.

## Risks And Test Signals
Risks include channel number mismatches, incomplete slave maps, and invalid filter parameters. Test signals include DMAengine slave channel lookup for every mapped peripheral, transfer completion, probe failure for missing maps, and concurrent channel allocation stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-mcf-edma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-mv_xor.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-mv_xor.h

## Purpose
This header defines platform data for Marvell XOR DMA engines. It supplies per-channel DMA capability masks to the `mv_xor` driver.

## Important APIs And Types
`MV_XOR_NAME` is the platform device name. `struct mv_xor_channel_data` contains a DMA capability mask, and `struct mv_xor_platform_data` points to an array of channel descriptors.

## Control Flow, State, And Persistence
There is no code flow. Platform code provides channel capability descriptions, which the driver exposes through DMAengine. State is static platform data.

## Dependencies And Integration Points
It depends on DMAengine capabilities and `linux/mbus.h`. Integration points include Marvell platform devices, DMAengine clients, and XOR/offload users such as RAID or memory operations.

## Risks And Test Signals
Incorrect capability masks can expose unsupported operations or hide usable acceleration. Test signals include DMAengine capability enumeration, XOR/memcpy offload tests, channel probe for each configured entry, and fallback behavior when no XOR channel is suitable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dma-mv_xor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dmtimer-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/dmtimer-omap.h

## Purpose
This header defines TI OMAP dual-mode timer platform data and the timer operation table exported to timer consumers. It abstracts request, configuration, PWM/capture, counter, interrupt, and clock operations.

## Important APIs And Types
`struct omap_dm_timer_ops` contains function pointers for requesting timers by device tree node, id, or any free timer; freeing; enable/disable; IRQ and interrupt mask control; clock access; start/stop; clock source; load/match/PWM/capture/prescaler configuration; counter/capture/status reads; and counter/status writes. `struct dmtimer_platform_data` carries OMAP1 timer-source callback, capability and errata flags, context-loss callback, and pointer to the ops table.

## Control Flow, State, And Persistence
The header defines a callback-driven control path: consumers request a timer, program load/match/PWM/capture state, start it, handle interrupts, and release it. Runtime state lives in the timer driver and hardware; context-loss count lets consumers detect lost hardware state across low-power transitions.

## Dependencies And Integration Points
It integrates OMAP timer users with platform timer drivers, device tree nodes, clocks, IRQs, PWM/capture consumers, and PM context-loss tracking.

## Risks And Test Signals
Risks include mismatched ops table, missing context restore after PM, incorrect source clock selection, and interrupt mask/status misuse. Test signals include timer request/free cycles, IRQ delivery, PWM output, capture reads, suspend/resume with context-loss detection, and errata-specific paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dmtimer-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ds620.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ds620.h

## Purpose
This header defines platform data for the DS620 temperature sensor and thermostat driver.

## Important APIs And Types
`struct ds620_platform_data` has one field, `pomode`, which selects thermostat output pin mode: always low, `PO_LOW`, or `PO_HIGH`.

## Control Flow, State, And Persistence
No control flow is implemented here. The I2C hwmon driver reads `pomode` at probe and programs the thermostat output behavior. State is sensor configuration in device registers plus static platform input.

## Dependencies And Integration Points
It includes Linux types and I2C headers and integrates board files or platform devices with the DS620 hwmon driver.

## Risks And Test Signals
Invalid `pomode` can produce wrong thermostat signaling. Test signals include probe with each supported mode, hwmon temperature reads, thermostat output behavior, and default behavior when platform data is absent or sparse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ds620.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dsa.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/dsa.h

## Purpose
This header defines legacy platform data for Distributed Switch Architecture switch chips. It describes port names, CPU/DSA links, associated network devices, and optional EEPROM size.

## Important APIs And Types
`DSA_MAX_PORTS` is 12. `struct dsa_chip_data` contains `netdev[DSA_MAX_PORTS]`, `eeprom_len`, and `port_names[DSA_MAX_PORTS]`. Port names use special strings: `"cpu"` for the CPU-facing port, `"dsa"` for inter-switch links, `NULL` for unused ports, and arbitrary names for user-facing physical ports.

## Control Flow, State, And Persistence
There is no executable flow. Platform data is consumed during switch registration to create the logical DSA topology and network interfaces. Runtime state lives in the DSA core and switch driver; EEPROM size describes optional persistent switch EEPROM access.

## Dependencies And Integration Points
The header forward-declares `struct device` and integrates legacy board files with the Linux DSA networking subsystem.

## Risks And Test Signals
Risks include incorrect CPU port designation, wrong DSA link labeling, missing netdev references, and exposing EEPROM operations with a bad size. Test signals include switch tree registration, port interface naming, traffic over CPU and DSA links, unused port suppression, and EEPROM read/write bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/dsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/edma.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/edma.h

## Purpose
This header documents and defines TI EDMA3 platform data. It describes event queues, controller/channel encoding, reserved resources, memcpy channels, queue priorities, crossbar channels, and DMA slave maps.

## Important APIs And Types
`enum dma_event_q` names EDMA event queues and the default queue. `EDMA_CTLR_CHAN()`, `EDMA_CTLR()`, `EDMA_CHAN_SLOT()`, and `EDMA_FILTER_PARAM()` encode controller/channel ids. `struct edma_rsv_info` lists reserved channel and slot ranges. `struct edma_soc_info` supplies default queue, reserved resources, memcpy channel list, queue-priority mapping, crossbar channels, slave map, and slave count.

## Control Flow, State, And Persistence
The header comments describe EDMA control flow: channels trigger transfers and reference PaRAM slots; slots describe transfers and may link to another slot; the channel controller maps logical events to transfer controllers; chained completions can trigger more work. The header itself is declarative. State is static SoC/resource topology plus runtime DMA descriptors in the driver.

## Dependencies And Integration Points
It integrates DaVinci/TI platform code with DMAengine, EDMA channel filters, peripheral slave maps, and consumers such as audio, MMC, SPI, and memcpy clients.

## Risks And Test Signals
Risks include reserved resource overlap, wrong controller/channel encoding, queue priority causing audio glitches, missing xbar mapping, and invalid slave map entries. Test signals include DMA channel filtering, transfer completion on each queue, linked PaRAM transfers, memcpy channel enumeration, reservation enforcement, and high-load peripheral DMA latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/edma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/elm.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/elm.h

## Purpose
This header defines the interface to TI's BCH Error Location Module used by OMAP NAND BCH ECC support. It describes ECC strength, error-vector results, and helper functions for configuring and decoding BCH errors.

## Important APIs And Types
`enum bch_ecc` selects BCH4, BCH8, or BCH16. `ERROR_VECTOR_MAX` is 8. `struct elm_errorvec` records whether a vector reported errors, whether errors were uncorrectable, the correctable error count, and up to 16 error locations. When `CONFIG_MTD_NAND_OMAP_BCH` is enabled, `elm_decode_bch_error_page()` and `elm_config()` are declared; otherwise inline stubs do nothing and return `-ENOSYS`.

## Control Flow, State, And Persistence
Consumers configure the ELM for ECC type, steps, step size, and syndrome size, then submit calculated ECC syndromes for page decode. The ELM driver fills error vectors for NAND correction. Runtime state is hardware configuration and per-page decode output only.

## Dependencies And Integration Points
It integrates OMAP NAND BCH code, MTD, and the ELM hardware driver. It uses Linux device pointers and conditional compilation for optional hardware support.

## Risks And Test Signals
Risks include mismatched BCH strength, wrong ECC step sizing, ignoring `-ENOSYS`, and mishandling uncorrectable vectors. Test signals include NAND read correction tests with injected bitflips, uncorrectable error reporting, build coverage with and without `CONFIG_MTD_NAND_OMAP_BCH`, and ECC layout compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/elm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/emc2305.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/emc2305.h

## Purpose
This header defines platform data for the EMC2305 multi-channel fan controller driver.

## Important APIs And Types
`EMC2305_PWM_MAX` is 5. `struct emc2305_platform_data` specifies maximum cooling state, active PWM channel count, PWM output and polarity masks, whether PWM settings are separate per channel, and per-channel minimum PWM and PWM frequency arrays.

## Control Flow, State, And Persistence
No code flow is present. The hwmon/thermal driver consumes the data at probe to configure channel availability, polarity, limits, and cooling-device behavior. State is hardware register configuration and thermal cooling state.

## Dependencies And Integration Points
It integrates board/platform description with the EMC2305 hwmon and thermal cooling subsystems.

## Risks And Test Signals
Risks include array index misuse beyond active `pwm_num`, inverted polarity, wrong minimum PWM causing fan stall, and cooling-state mismatch. Test signals include hwmon PWM reads/writes, thermal cooling state transitions, per-channel frequency programming, fan tach response, and sparse platform-data defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/emc2305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/emif_plat.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/emif_plat.h

## Purpose
This header defines TI EMIF platform data for DDR memory controller setup. It captures low-power policy, hardware capabilities, IP/PHY revisions, DDR device geometry, timing tables, and board-specific custom configuration.

## Important APIs And Types
Constants define EMIF low-power modes, hardware capability bits, EMIF IP revisions (`EMIF_4D`, `EMIF_4D5`), PHY types, and custom config masks. `struct ddr_device_info` describes memory type, density, bus width, CS1 use, calibration resistor topology, and manufacturer. `struct emif_custom_configs` describes requested low-power mode, performance/power timeout choices, frequency threshold, and temperature polling interval. `struct emif_platform_data` ties together capabilities, DDR info, LPDDR2 timings/min cycles, custom configs, IP revision, and PHY type.

## Control Flow, State, And Persistence
The EMIF driver consumes this at probe and during frequency/power management to program timing and low-power registers. Custom config masks determine which policies override driver defaults. State persists in hardware registers across runtime until context loss or reprogramming; this header stores only the platform description.

## Dependencies And Integration Points
It references LPDDR2 timing/min-tck structures, OMAP/TI platform code, memory-controller drivers, PM/OPP frequency management, and temperature alert polling.

## Risks And Test Signals
Incorrect DDR geometry or timing data can cause memory instability. Low-power thresholds can trade performance for power or trigger resume failures. Test signals include memory stress across supported frequencies, suspend/resume and context-loss restore, temperature polling behavior, low-power-mode register programming, and validation with both default and custom timing data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/emif_plat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/g762.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/g762.h

## Purpose
This header defines optional platform data for the G762 fan controller driver, allowing board code to override bootloader-provided fan settings.

## Important APIs And Types
`struct g762_platform_data` carries `fan_startv`, `fan_gear_mode`, `pwm_polarity`, and `clk_freq`.

## Control Flow, State, And Persistence
No executable flow exists. The driver reads this sparse platform data at probe and applies specified attributes, while unspecified values may fall back to defaults. The comments warn that sparse data can still overwrite bootloader-installed attributes with defaults.

## Dependencies And Integration Points
It integrates platform/board setup with the G762 hwmon fan driver.

## Risks And Test Signals
Risks include unintentionally overriding firmware fan policy, wrong polarity, and incorrect clock frequency leading to wrong RPM/PWM conversion. Test signals include probe with empty and populated platform data, fan start voltage behavior, PWM polarity verification, RPM readings, and preservation of firmware defaults where intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/g762.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpio-htc-egpio.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/gpio-htc-egpio.h

## Purpose
This header defines platform data for HTC's simple EGPIO GPIO/IRQ extender. It describes register ranges that become GPIO chips plus IRQ acknowledgement behavior.

## Important APIs And Types
`HTC_EGPIO_OUTPUT` and `HTC_EGPIO_INPUT` are descriptive all-output/all-input masks. `struct htc_egpio_chip` defines register start, GPIO base, GPIO count, direction bitfield, and initial output values. `struct htc_egpio_platform_data` defines bus/register width, IRQ base/count, ack inversion, ack register, chip descriptor array, and descriptor count.

## Control Flow, State, And Persistence
The driver consumes chip descriptors at probe to create gpiochips, initialize direction/output state, and wire IRQ handling. IRQ flow depends on `invert_acks`: some hardware acknowledges by writing zero instead of one. State is hardware register state and Linux GPIO/IRQ registration.

## Dependencies And Integration Points
It integrates HTC board files with gpiochip and irqchip registration for external GPIO expanders.

## Risks And Test Signals
Risks include wrong register width or bus alignment, GPIO base overlap, bad direction masks, and inverted IRQ ack configuration causing interrupt storms or lost IRQs. Test signals include GPIO direction/value tests, initial output state verification, IRQ trigger/ack tests, and multi-chip range registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpio-htc-egpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpio-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/gpio-omap.h

## Purpose
This header defines register offsets and platform data for OMAP GPIO banks across OMAP1, OMAP7xx, OMAP16xx, OMAP2+, and OMAP4 variants. It lets one GPIO driver handle multiple register layouts and PM capabilities.

## Important APIs And Types
The file declares many register offset constants for MPUIO and SoC-specific GPIO revisions, `OMAP34XX_NR_GPIOS`, and `OMAP_MAX_GPIO_LINES`. `struct omap_gpio_reg_offs` maps logical operations to actual register offsets and includes `irqenable_inv`. `struct omap_gpio_platform_data` supplies bank type, bank width, bank stride, debounce clock requirement, context-loss behavior, MPUIO flag, non-wakeup GPIO mask, register-offset table, and optional context-loss callback.

## Control Flow, State, And Persistence
The header is declarative. The GPIO driver uses the offset table to read/write data, direction, debounce, IRQ status/mask, wakeup, edge/level detect, and set/clear dataout registers. Runtime state includes configured GPIO direction/value/IRQ modes and saved context for banks that lose context.

## Dependencies And Integration Points
It integrates OMAP platform devices, memory-mapped I/O, GPIO, IRQ, debounce clock, and PM context-loss handling. The assembler guard allows register constants to be reused outside C contexts.

## Risks And Test Signals
Risks include wrong offset table for a bank, inverted IRQ enable semantics, missing debounce clock, non-wakeup GPIO mask errors, and failed context restore after idle/suspend. Test signals include GPIO line read/write, IRQ edge and level detection, debounce behavior, wakeup source tests, MPUIO-specific register access, and suspend/resume context restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpio-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpio/gpio-amd-fch.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/gpio/gpio-amd-fch.h

## Purpose
This header defines AMD FCH GPIO platform data and register-index constants for the AMD FCH GPIO driver.

## Important APIs And Types
`AMD_FCH_GPIO_DRIVER_NAME` names the driver. Register constants identify supported GPIO registers such as GPIO49, GPIO50, GPIO51, DEVSLP pins, speaker, GE pins, and `AMT_FCH_GPIO_REG_GEVT22`. `struct amd_fch_gpio_pdata` contains the number of GPIO entries, an array of register indices, and an array of GPIO names.

## Control Flow, State, And Persistence
There is no executable control flow. Platform code lists which FCH GPIO registers should be exposed; the driver maps those registers into GPIO lines and labels them. State is chipset register configuration and gpiochip registration.

## Dependencies And Integration Points
It integrates platform data with the AMD FCH GPIO driver and Linux GPIO framework.

## Risks And Test Signals
Risks include mismatched `gpio_num` and array lengths, wrong register constants, typo-preserved constants, and name ordering mismatches. Test signals include gpiochip line count/names, read/write on each listed register, direction support, and probe failure on invalid platform arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpio/gpio-amd-fch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpio_backlight.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/gpio_backlight.h

## Purpose
This header defines platform data for a simple GPIO-controlled backlight.

## Important APIs And Types
`struct gpio_backlight_platform_data` contains a single `struct device *dev`, used as a back-reference by the backlight driver.

## Control Flow, State, And Persistence
No executable flow is present. The driver receives the platform data at probe and uses the associated device context while controlling a GPIO-backed backlight. Runtime state is the backlight brightness/on-off state in the driver and GPIO.

## Dependencies And Integration Points
It forward-declares `struct device` and integrates simple board/platform data with the backlight subsystem and GPIO descriptors.

## Risks And Test Signals
Risks are limited: stale device pointers or missing GPIO resources can break probe or power control. Test signals include backlight registration, brightness/on-off toggles, suspend/resume behavior, and device-managed resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpio_backlight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpmc-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/gpmc-omap.h

## Purpose
This header defines OMAP General-Purpose Memory Controller platform data. It describes chip-select timing, device timing, bus settings, wait-pin policy, and child devices attached to each GPMC chip select.

## Important APIs And Types
`GPMC_CS_NUM` is 8. `struct gpmc_bool_timings` captures extra delay/granularity booleans. `struct gpmc_timings` stores controller timings in nanoseconds, with `sync_clk` in picoseconds, and embeds boolean timing flags. `struct gpmc_device_timings` stores device datasheet timings in picoseconds/cycles plus extra-delay flags. Constants define burst lengths, device widths, multiplexing modes, wait-pin polarity, and invalid sentinel values. `struct gpmc_settings` describes burst, NAND, sync, wait, width, mux, and wait-pin settings. `struct gpmc_omap_cs_data` binds one chip select to settings, timings, child platform device, and platform-data size. `struct gpmc_omap_platform_data` contains all chip selects.

## Control Flow, State, And Persistence
The GPMC driver computes register values from device timing and settings, programs chip-select registers, and creates child devices. State lives in GPMC registers and child device registration; no persistent storage is managed here.

## Dependencies And Integration Points
It integrates OMAP board data with GPMC, NAND, NOR, FPGA, Ethernet, or other memory-mapped child devices using platform devices and timing translation.

## Risks And Test Signals
Risks include unit confusion between ns/ps/cycles, invalid wait-pin polarity, bad chip-select validity, and incorrect timing causing memory bus failures. Test signals include register timing dumps, child-device probe, NAND/NOR read/write stress, sync/asynchronous mode tests, wait-pin behavior, and multi-CS coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gpmc-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gsc_hwmon.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/gsc_hwmon.h

## Purpose
This header defines platform data for the Gateworks System Controller hwmon driver. It describes ADC/fan channels, conversion modes, voltage references, and channel names.

## Important APIs And Types
`enum gsc_hwmon_mode` distinguishes temperature, 24-bit voltage, raw voltage, 16-bit voltage, fan, and max modes. `struct gsc_hwmon_channel` contains I2C register offset, mode, name, voltage offset, and two-resistor divider values. `struct gsc_hwmon_platform_data` contains channel count, ADC resolution, voltage reference, fan register base, and a counted flexible array of channels.

## Control Flow, State, And Persistence
The hwmon driver reads the channel array at probe, then periodically reads I2C registers and converts raw values according to mode, reference, resolution, divider, and offset. State is static channel description plus live sensor readings.

## Dependencies And Integration Points
It integrates platform data with hwmon sysfs, I2C register access, and board-specific voltage/fan monitoring topology.

## Risks And Test Signals
Risks include wrong channel count for the flexible array, incorrect voltage divider math, bad ADC resolution/reference, and register overlap. Test signals include hwmon channel enumeration, temperature/voltage/fan conversion checks against known inputs, boundary ADC values, and counted-by build diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/gsc_hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/hirschmann-hellcreek.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/hirschmann-hellcreek.h

## Purpose
This header defines platform data for the Hirschmann Hellcreek TSN switch driver.

## Important APIs And Types
`struct hellcreek_platform_data` contains switch name, port count, speed mode flag (`is_100_mbits`), Qbv support for front TSN ports and CPU port, Qbu support, and module id.

## Control Flow, State, And Persistence
The header has no executable flow. The switch driver uses these fields at probe to size ports, label the device, configure speed-specific behavior, and expose TSN features. Runtime state resides in the switch driver and hardware.

## Dependencies And Integration Points
It depends on Linux types and integrates platform devices with the Hellcreek DSA/TSN switch driver, including time-aware shaping and frame preemption capabilities.

## Risks And Test Signals
Risks include wrong port count, feature flags that expose unsupported TSN controls, and speed-mode mismatch. Test signals include switch probe, port creation, link speed verification, Qbv/Qbu control availability, traffic forwarding, and module-id reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/hirschmann-hellcreek.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/hsmmc-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/hsmmc-omap.h

## Purpose
This header defines OMAP HSMMC platform data and device attributes for MMC/SD/eMMC controllers.

## Important APIs And Types
Flags describe dual-voltage support, broken multiblock read erratum, and missing software wakeup. `struct omap_hsmmc_dev_attr` stores controller flags. `struct omap_hsmmc_platform_data` includes back-link device, max bus frequency, controller flags, register offset deviation, MMC capability and PM capability masks, nonremovable and regulator-off quirks, feature bits for PBIAS/reset/HSPE support, version string, name, and OCR mask.

## Control Flow, State, And Persistence
No code flow is defined here. The MMC host driver consumes the platform data during probe, sets caps/OCR/frequency limits, applies errata, and manages regulator behavior. Runtime state is MMC host/card state and hardware registers.

## Dependencies And Integration Points
It integrates OMAP platform data with the Linux MMC core, regulators/PBIAS, PM wake capabilities, and hardware-module attributes.

## Risks And Test Signals
Risks include advertising unsupported voltage, missing broken-multiblock workaround, disabling eMMC regulator incorrectly, and wrong register offset. Test signals include card detect/probe, single and multiblock transfers, voltage switching, suspend/resume wake behavior, eMMC power sequencing, and max-frequency enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/hsmmc-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/huawei-gaokun-ec.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/huawei-gaokun-ec.h

## Purpose
This header declares the common API for the Huawei Matebook E Go / Gaokun embedded controller driver and its child power-supply and UCSI functions.

## Important APIs And Types
Constants define UCSI CCI/MSGIN read sizes, write size, no-port-update sentinel, smart-charge payload size, module and child device names. Forward declarations cover `gaokun_ec`, `gaokun_ucsi_reg`, and `notifier_block`. Common APIs include notifier registration, raw EC read/write/read-byte helpers. Power-supply APIs include multi-read, byte/word inline reads, smart-charge get/set, and smart-charge enable get/set. UCSI APIs include read/write, register snapshot retrieval, and PAN acknowledge by port.

## Control Flow, State, And Persistence
The header declares synchronous request/response operations around an EC command transport. Children call common helpers to read power-supply registers or UCSI state. Smart-charge settings are likely persistent or semi-persistent in EC firmware, but persistence is implemented by the EC/driver, not the header. Notifiers provide event-driven updates.

## Dependencies And Integration Points
It integrates the Gaokun EC core with notifier consumers, power_supply child device, and UCSI Type-C/USB-C subsystem. The inline word read casts the response buffer to `u8 *`, so callers must account for EC endianness/packing expectations.

## Risks And Test Signals
Risks include fixed-size UCSI payload mismatches, invalid smart-charge payload length, notifier lifetime issues, endian assumptions in word reads, and port id handling for PAN ACK. Test signals include raw EC read/write transactions, power-supply register reads, smart-charge get/set round trip, UCSI PPM command flow, notifier delivery, and invalid-port error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/huawei-gaokun-ec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-gpio.h

## Purpose
This header defines platform data for the GPIO bit-banged I2C adapter driver.

## Important APIs And Types
`struct i2c_gpio_platform_data` contains `udelay`, `timeout`, and bitfields describing SDA/SCL electrical behavior: open-drain, output-only, and no-pullup for each line. The comment states SCL frequency is approximately `500 / udelay` kHz.

## Control Flow, State, And Persistence
The i2c-gpio driver uses this data to choose bit timing, clock-stretch timeout, and whether lines can be released/read for open-drain semantics. Runtime state is adapter transfer sequencing over GPIOs; no persistence is defined.

## Dependencies And Integration Points
It integrates board-specific GPIO wiring with the Linux I2C adapter layer and GPIO API.

## Risks And Test Signals
Risks include configuring push-pull as open-drain or vice versa, missing pull-ups, output-only lines that prevent proper arbitration/readback, and bad timing values. Test signals include I2C bus scan, transfers with clock-stretching slaves, waveform timing, no-pullup behavior, and timeout handling when SCL is held low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-imx.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-imx.h

## Purpose
This header defines platform data for the Freescale/NXP i.MX I2C driver.

## Important APIs And Types
`struct imxi2c_platform_data` contains a single `bitrate` field, measured in Hz.

## Control Flow, State, And Persistence
There is no executable flow. The i.MX I2C driver reads `bitrate` at probe or setup time and programs controller clock dividers accordingly. Runtime state is I2C controller configuration and active transfers.

## Dependencies And Integration Points
It integrates i.MX board/platform data with the Linux I2C controller driver and clock framework.

## Risks And Test Signals
Risks include unsupported bitrate values, incorrect parent clock assumptions, and transfer failures at too-high speeds. Test signals include bus frequency measurement, standard/fast-mode device transfers, arbitration/NAK handling, and probe behavior when bitrate is zero or unspecified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-imx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-mux-gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-mux-gpio.h

## Purpose
This header defines platform data for an I2C mux controlled by GPIO lines.

## Important APIs And Types
`I2C_MUX_GPIO_NO_IDLE` means no specific idle mux state. `struct i2c_mux_gpio_platform_data` contains parent adapter number, base adapter number for child buses, array of GPIO bitmask values, number of mux positions, idle bitmask, and settle time after selection.

## Control Flow, State, And Persistence
The mux driver selects a child bus by writing the corresponding GPIO bitmask, waits `settle_time`, performs transfers through the parent adapter, and optionally writes the idle state when done. State is the current GPIO mux selection.

## Dependencies And Integration Points
It integrates platform data with the I2C mux core, parent I2C adapters, and GPIO-controlled board multiplexers.

## Risks And Test Signals
Risks include wrong parent adapter number, duplicate child bus numbers, mismatched values array length, missing settle delay, and unsafe idle state. Test signals include child adapter creation, transfers on every mux position, idle-state verification, GPIO waveform checks, and concurrent child bus access serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-mux-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-mux-reg.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-mux-reg.h

## Purpose
This header defines platform data for an I2C mux selected by writing a memory-mapped register.

## Important APIs And Types
`struct i2c_mux_reg_platform_data` contains parent and base adapter numbers, per-channel register values, channel count, endian flag, write-only flag, optional idle value and `idle_in_use`, MMIO register pointer, and register size.

## Control Flow, State, And Persistence
The mux driver selects a bus by writing one value to the mapped register, using endian and width information; if configured it writes idle value after use. If `write_only` is set, it must not attempt read-modify-write or verification reads. State is current hardware mux register value.

## Dependencies And Integration Points
It integrates I2C mux core, platform MMIO resources, and board-specific register mux hardware.

## Risks And Test Signals
Risks include wrong register size/endian, unsafe reads from write-only hardware, invalid MMIO pointer lifetime, and idle value selecting an active conflicting bus. Test signals include child adapter transfers, register write tracing, big/little-endian selection, write-only mode, idle behavior, and invalid channel handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-mux-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-ocores.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-ocores.h

## Purpose
This header defines platform data for the OpenCores I2C controller driver.

## Important APIs And Types
`struct ocores_i2c_platform_data` includes register shift, register I/O width, input clock in kHz, target bus clock in kHz, big-endian register flag, number of attached board devices, and pointer to an `i2c_board_info` array.

## Control Flow, State, And Persistence
No executable flow is included. The driver consumes this data to map register offsets/widths, compute timing divisors, configure endian-aware accessors, register the adapter, and instantiate listed I2C devices. Runtime state is controller registers and I2C adapter/device registration.

## Dependencies And Integration Points
It integrates OpenCores I2C platform devices with Linux I2C core, board-info device instantiation, and MMIO accessor selection.

## Risks And Test Signals
Risks include incorrect register shift or I/O width, clock mismatch causing wrong bus speed, endian mismatch, and stale device list lengths. Test signals include adapter registration, measured bus frequency, transfers to board-info devices, endian/access-width variants, and error handling for NAK/arbitration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-ocores.h -->
