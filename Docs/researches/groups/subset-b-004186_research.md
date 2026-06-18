# subset-b-004186 research

Grouped research report for the requested Linux media remote-controller and SPI adapter files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/nuvoton-cir.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/nuvoton-cir.h

Purpose: private hardware definition header for the Nuvoton W83667HG/W83677HG-I consumer IR driver. It centralizes Super I/O IDs, CIR and CIR wake register offsets, FIFO encodings, sample-period constants, wake comparison sizing, and the runtime state structures consumed by `nuvoton-cir.c`.

Important APIs, types, and constants: `enum nvt_chip_ver` identifies supported chip IDs; `struct nvt_chip` maps names to versions; `struct nvt_dev` holds the `rc_dev`, spinlock, RX packet buffer, EFER register pair, CIR base/IRQ resources, chip revision fields, and carrier. Debug macros `nvt_dbg*` are controlled by the file-local `debug` variable. Key register groups include CIR data/control registers, CIR wake registers, Super I/O config registers, logical-device IDs, pinmux bits, MCE wake length thresholds, `SAMPLE_PERIOD`, `MIN_CARRIER`, `MAX_CARRIER`, and `WAKEUP_MAX_SIZE`.

Control flow: this header has no executable flow, but it defines the contract used by the driver when entering Super I/O extended function mode, selecting logical devices, enabling CIR/CIR wake resources, programming RX/TX FIFOs, interpreting hardware packet bytes, and comparing stored wake patterns.

State and persistence: all state is runtime and hardware-backed. `struct nvt_dev` stores volatile driver state and discovered hardware resources. CIR and wake registers persist only while the Super I/O device retains power/configuration. Wake comparison constants describe firmware/hardware wake pattern storage, not filesystem persistence.

Dependencies and integration points: depends on Linux spinlock/ioctl headers and `media/rc-core.h` constants via includers. It integrates the Nuvoton driver with rc-core raw event reporting, Super I/O logical-device configuration, ACPI/PME wake routing, and MCE-compatible wake pattern encoding.

Risks and edge cases: the header defines `static int debug`, so it is intended for one C translation unit; multiple inclusions into separate C files would create separate debug variables. Several timing and FIFO trigger choices are compile-time `FIXME` constants rather than runtime tunables. Floating-looking macro `CIR_SAMPLE_LOW_INACCURACY 0.85` is not an integer constant and must only be used in contexts that tolerate floating arithmetic. Wake matching uses tight fixed MCE length bands, so nonstandard remotes can fail wake programming.

Test signals: compile coverage of `nuvoton-cir.c`, probe on each supported chip ID, Super I/O resource discovery, RX/TX FIFO interrupt behavior, sample-period timing against logic-analyzer captures, carrier limits, and suspend/wake using the 65-byte wake comparison path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/nuvoton-cir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/pwm-ir-tx.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/pwm-ir-tx.c

Purpose: implements a platform `RC_DRIVER_IR_RAW_TX` transmitter that emits raw IR pulse/space durations by toggling a PWM device. It supports generic `pwm-ir-tx` and `nokia,n900-ir` device-tree compatibles.

Important APIs and functions: `struct pwm_ir` stores the PWM handle, optional hrtimer/completion state, carrier, duty cycle, and active transmit buffer cursor. rc-core callbacks are `pwm_ir_set_duty_cycle`, `pwm_ir_set_carrier`, `pwm_ir_tx_sleep`, and `pwm_ir_tx_atomic`; platform binding is through `pwm_ir_probe` and `module_platform_driver`.

Control flow: probe allocates private state, obtains the PWM, initializes 38 kHz/50 percent defaults, allocates an rc-core TX-only device, then chooses either sleepable or atomic transmission depending on `pwm_might_sleep()`. The sleepable path applies PWM state and sleeps until each target edge. The atomic path stores a stack `pwm_state` pointer, starts an hrtimer, toggles PWM state in `pwm_ir_timer`, advances the expiry by each duration, and completes when all entries are consumed.

State and persistence: state is per-device and devm-managed. Carrier and duty cycle persist only while the platform device is bound. Active transmit state lives in `struct pwm_ir` for the duration of one synchronous `tx_ir` call; hardware PWM state is disabled at the end of sleepable sends and after the atomic timer reaches completion.

Dependencies and integration points: depends on Linux PWM, hrtimer, completion, platform/OF, and rc-core TX APIs. It integrates with rc-core through `devm_rc_allocate_device`, `devm_rc_register_device`, `s_tx_carrier`, `s_tx_duty_cycle`, and `tx_ir`.

Risks and edge cases: the atomic timer applies PWM state before checking whether `txbuf_index >= txbuf_len`, so completion can perform one extra state application with the final index. The atomic path points `pwm_ir->state` at a stack variable while waiting synchronously; it relies on the timer completing before return. Sleepable PWM providers are explicitly less accurate. There is no remove hook to cancel a possible in-flight hrtimer, though `tx_ir` waits synchronously. A zero carrier is rejected, but duty cycle range is not locally constrained.

Test signals: device-tree probe, rc-core registration as TX-only, carrier/duty sysfs or lirc ioctl updates, oscilloscope validation of carrier period/duty and pulse train durations for both sleepable and atomic PWM providers, and unload/removal under no active transmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/pwm-ir-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/rc-core-priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/rc-core-priv.h

Purpose: private rc-core header that connects the public `media/rc-core.h` API to internal raw IR decoding, LIRC, and BPF support. It defines raw handler/client state and shared helpers used by decoders, encoders, `rc-main.c`, and `rc-ir-raw.c`.

Important APIs and types: exported internal lifecycle declarations include `rc_open`, `rc_close`, `ir_raw_event_prepare/register/unregister/free`, `ir_raw_handler_register/unregister`, `ir_raw_load_modules`, and `ir_raw_init`. `struct ir_raw_handler` describes decoder/encoder modules, protocol bitmask, carrier, timeout, and optional per-device registration hooks. `struct ir_raw_event_ctrl` owns each raw device FIFO, worker thread, edge timer, last event timestamp, decoder state structs for configured protocol decoders, and optional BPF program array.

Control flow: rc-core allocates `ir_raw_event_ctrl` for raw devices, decoder modules register `ir_raw_handler` entries, and `rc-ir-raw.c` uses the shared helpers to queue, decode, encode, and tear down raw events. Inline helpers implement timing comparisons, transition checks, duration reduction, normal-event classification, and raw event construction.

State and persistence: state is in-memory only. The `ir_raw_event_ctrl` FIFO buffers up to `MAX_IR_EVENT_SIZE` pulse/space transitions per raw device. Protocol decoder substates persist only while the rc device and decoder modules remain registered. LIRC and BPF members are compiled in conditionally and have no on-disk persistence.

Dependencies and integration points: depends on Linux slab allocation, UAPI BPF declarations, and public rc-core types. It is the internal integration point between rc-core, raw IR protocol decoder modules, LIRC character-device support, and optional BPF LIRC mode2 filters.

Risks and edge cases: the header exposes many private fields to decoder implementations, so structure changes can break multiple modules. Timing helpers use unsigned arithmetic and assume margins smaller than target durations. Conditional decoder state means build configuration changes alter `struct ir_raw_event_ctrl` layout. Stubbed LIRC/BPF functions hide feature absence from callers, so tests must cover both enabled and disabled configs.

Test signals: allmodconfig and minimal-config builds, raw decoder module load/unload, LIRC enabled/disabled builds, BPF_LIRC enabled builds, FIFO overflow behavior, protocol encoder helper tests, and raw handler registration under active devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/rc-core-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/rc-ir-raw.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/rc-ir-raw.c

Purpose: implements rc-core raw IR event handling. It queues pulse/space events from drivers, runs decoder handlers in a per-device kernel thread, exposes encoder helper routines, manages raw protocol module registration, and bridges raw events to LIRC/BPF paths.

Important APIs and functions: driver-facing exports are `ir_raw_event_store`, `ir_raw_event_store_edge`, `ir_raw_event_store_with_timeout`, `ir_raw_event_store_with_filter`, `ir_raw_event_set_idle`, and `ir_raw_event_handle`. Encoder exports include `ir_raw_gen_manchester`, `ir_raw_gen_pd`, `ir_raw_gen_pl`, `ir_raw_encode_scancode`, and `ir_raw_encode_carrier`. Lifecycle functions are `ir_raw_event_prepare`, `ir_raw_event_register`, `ir_raw_event_unregister`, `ir_raw_event_free`, `ir_raw_handler_register`, and `ir_raw_handler_unregister`.

Control flow: `ir_raw_event_prepare` allocates per-device raw state and installs `change_protocol`. Drivers push events into the kfifo from IRQ or process context, optionally merging samples and entering idle through `ir_raw_event_store_with_filter`. `ir_raw_event_handle` wakes the per-device thread, which drains the FIFO, checks event sanity, runs matching raw handlers under `ir_raw_handler_lock`, forwards events to LIRC, and remembers the previous event. Edge-only hardware uses a timer to batch wakeups and synthesize timeout events. Protocol changes call handler raw register/unregister hooks and adjust receive timeout based on enabled handlers.

State and persistence: global state includes raw client and handler lists plus an atomic available-protocol bitmask. Per-device state includes the raw FIFO, worker thread, edge timer, previous/current events, idle state via the parent `rc_dev`, and conditional decoder/BPF state. All state is volatile and removed during unregister/free.

Dependencies and integration points: depends on kthreads, kfifo, timers, mutexes, kmod autoloading from `rc-main.c`, LIRC hooks, and `rc-core-priv.h`. Protocol decoder modules register `ir_raw_handler` entries here. rc drivers call the event-store APIs from hardware interrupt paths.

Risks and edge cases: FIFO overflow drops IR samples and only reports `-ENOSPC` to the caller. Handler decode runs under the global raw handler mutex, so slow decoders can block protocol changes and other raw clients. `ir_raw_event_unregister` stops the thread and deletes the edge timer but leaves `dev->raw` allocated until release, relying on lock ordering to protect BPF queries. Edge timeout synthesis can enqueue zero-duration or repeated events if hardware timestamps are erratic. Encoder helpers write partial buffers on `-ENOBUFS`.

Test signals: raw receiver drivers delivering pulses, edge-only drivers generating timeout events, protocol sysfs enable/disable, decoder module autoload/unload, LIRC mode2 output, BPF attach/detach while unregistering, FIFO saturation tests, and encoder round trips for NEC/RC5/RC6/JVC/Sony protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/rc-ir-raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/rc-loopback.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/rc-loopback.c

Purpose: provides a virtual rc-core loopback device for debugging. It accepts transmitted raw IR durations through rc-core TX callbacks and feeds them back into the raw receive pipeline without physical hardware.

Important APIs and functions: `struct loopback_dev` stores loopback configuration. rc-core callbacks include `loop_set_tx_mask`, `loop_set_tx_carrier`, `loop_set_tx_duty_cycle`, `loop_set_rx_carrier_range`, `loop_tx_ir`, `loop_set_idle`, `loop_set_wideband_receiver`, `loop_set_carrier_report`, and `loop_set_wakeup_filter`. Module lifecycle is `loop_init` and `loop_exit`.

Control flow: module init allocates an `RC_DRIVER_IR_RAW` device with both RX and TX capabilities, all IR decoder protocols, all encoder wake protocols, timeout/filter callbacks, and default carrier/mask values. `loop_tx_ir` rejects delivery when TX carrier or mask is incompatible with current RX settings; otherwise it converts alternating TX durations into raw pulse/space events, optionally emits carrier reports, appends a timeout-length silence, and wakes raw decoders. Wakeup filter setting encodes the requested wake scancode as raw IR and loops it back into the receiver.

State and persistence: a single static `loopdev` holds the virtual device and settings. State persists only while the module is loaded. No hardware or filesystem persistence is involved.

Dependencies and integration points: depends on rc-core raw RX/TX APIs and the protocol encoder registry. It integrates with sysfs/LIRC test workflows, carrier-report paths, wakeup filter encoding, and raw decoder modules.

Risks and edge cases: `loop_set_tx_mask` returns `2` for invalid masks rather than a negative errno, which is unusual. Carrier, mask, and wideband settings are not locked independently, relying on rc-core callback serialization. The overflow simulation only triggers for pulses longer than 50 ms. Wake filter loopback accepts partial encodings on `-ENOBUFS`, which is useful for debugging but can surprise strict tests.

Test signals: module load creates one `rc` device, `ir-ctl` transmit loops into decoders, carrier range and mask mismatch suppress events, carrier report emission, wakeup filter encoding through sysfs, overflow simulation with long pulses, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/rc-loopback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/rc-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/rc-main.c

Purpose: core remote-controller module. It manages keymap registration, scancode-to-keycode tables, input device event generation, rc class/sysfs devices, protocol/filter attributes, LIRC registration sequencing, rc device allocation/registration, and module init/exit.

Important APIs and functions: public exports include `rc_map_get/register/unregister`, `rc_g_keycode_from_table`, `rc_keyup`, `rc_repeat`, `rc_keydown`, `rc_keydown_notimeout`, `rc_allocate_device`, `rc_free_device`, `devm_rc_allocate_device`, `rc_register_device`, `devm_rc_register_device`, and `rc_unregister_device`. Internal groups cover keymap allocation/resizing/updating, input `getkeycode`/`setkeycode`, protocol parsing/autoloading, filter validation, wakeup protocol sysfs, open/close reference counting, and rc class lifecycle.

Control flow: driver code allocates an `rc_dev`, fills capabilities/callbacks/map name, then calls `rc_register_device`. Registration assigns a minor, prepares raw state for raw drivers, loads/installs keymaps and default protocols, adds the rc class device, registers LIRC before the input device, registers input, and starts raw event processing. Keydown/repeat paths look up scancodes, emit MSC_SCAN/EV_KEY events, update timers, and send LIRC scancode events. Sysfs protocol writes parse `+proto`, `-proto`, or replacement requests, autoload raw decoder modules, call driver `change_protocol`, and refresh filters.

State and persistence: global state includes registered keymap list, rc feedback LED trigger, and the IDA of rc minors. Per-device state includes sorted keymap table, enabled protocols, filters, wakeup settings, timers, user count, last key state, input device, raw state, and class device. State is volatile; user keymap edits and sysfs settings do not persist across unregister.

Dependencies and integration points: integrates Linux input, device class/sysfs, LED triggers, kmod module autoload, LIRC, optional CEC rc map, raw IR internals, and driver callbacks for hardware protocol/filter/timeout/open/close operations.

Risks and edge cases: keytable resizing happens under spinlock and can fail during input keymap updates. Protocol autoload sleeps and assumes decoder modules register soon after load. Registration ordering is deliberate; changing LIRC/input sequencing can expose userspace opens before LIRC is ready. `rc_unregister_device` calls driver close for active users while unregistering, so driver close paths must tolerate disappearing hardware. Wakeup filter validation depends on one active wake protocol and rejects masked raw-encoded wake filters.

Test signals: rc class creation, keymap module autoload, EVIOCGKEY/EVIOCSKEY updates, protocol sysfs changes, filter and wakeup_filter sysfs validation, raw and scancode driver registration/unregistration, LIRC device presence, repeat/keyup timing per protocol, CEC-specific repeat behavior, devm cleanup, and concurrent open/unplug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/rc-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/redrat3.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/redrat3.c

Purpose: USB rc-core driver for RedRat3 and RedRat3-II IR transceivers. It receives narrowband and wideband IR, reports optional carrier information, transmits encoded IR through the device firmware protocol, exposes a feedback LED, and controls capture parameters.

Important APIs and functions: packet structures are `redrat3_header`, `redrat3_irdata`, and `redrat3_error`; device state is `struct redrat3_dev`. Major flows include `redrat3_reset`, `redrat3_get_firmware_rev`, `redrat3_enable_detector`, `redrat3_handle_async`, packet accumulation helpers, `redrat3_process_ir_data`, timeout get/set, `redrat3_transmit_ir`, `redrat3_set_tx_carrier`, `redrat3_wideband_receiver`, LED callbacks, `redrat3_init_rc_dev`, USB probe/disconnect, and suspend/resume.

Control flow: probe discovers bulk-in narrow/wide and bulk-out endpoints, allocates shared coherent input buffer and URBs, resets/configures firmware parameters, creates LED/learning URBs, registers an `RC_DRIVER_IR_RAW` rc device, then enables detector capture and submits receive URBs. Incoming URBs are accumulated until a complete firmware packet is available; signal packets map length-table indices to alternating pulse/space raw events and append a trailing timeout. TX converts microsecond durations into RedRat length table entries and sigdata indices, bulk-writes the packet, then sends a vendor command to transmit.

State and persistence: per-device state holds endpoint descriptors, URBs, coherent buffer, current packet assembly, transmit flag, carrier, LED/learning control state, rc device, and USB identity strings. Firmware parameters such as length fuzz, minimum pause, periods-to-measure-carrier, max lengths, and timeout are programmed at runtime and are not persisted by the driver.

Dependencies and integration points: depends on USB bulk/control transfers, rc-core raw RX/TX, LED class, unaligned big-endian helpers, and keymap `RC_MAP_HAUPPAUGE`. Wideband mode integrates with rc-core carrier reports through `s_carrier_report`.

Risks and edge cases: narrow and wide URBs share one coherent input buffer, so simultaneous completions would race on packet data. TX is guarded only by a boolean, not a lock. Packet assembly resets on malformed length but relies on firmware length fields. Probe error paths unregister LED but may need careful review after rc device creation failures. Module parameters accept documented ranges but are not range-validated before firmware writes. Hardware timing conversion clamps large durations and deduplicates exact converted lengths only.

Test signals: USB probe for both product IDs, endpoint validation, firmware parameter writes, continuous receive on narrowband, wideband carrier reports, `ir-ctl` transmit, timeout get/set, LED feedback blink, suspend/resume URB resubmission, disconnect during active receive/TX, and malformed packet/error-code handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/redrat3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/serial_ir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/serial_ir.c

Purpose: legacy serial-port IR receiver/transmitter driver using modem-control pins on 8250-compatible UARTs. It supports homebrew, IRdeo, IRdeo Remote, AnimaX, and IgorPlug hardware variants.

Important APIs and functions: `struct serial_ir_hw` describes per-hardware pin polarity, UART control values, optional transmit callbacks, and lock. `struct serial_ir` stores timestamp, rc device, synthetic platform device, timeout timer, carrier, and duty cycle. Core functions include `hardware_init_port`, `serial_ir_irq_handler`, `frbwrite`, `serial_ir_timeout`, `serial_ir_probe`, open/close, TX helpers, suspend/resume, and module parameter initialization.

Control flow: module init validates `type`, fills default I/O and IRQ, registers a platform driver and synthetic platform device. Probe allocates a raw rc device, requests IRQ and I/O or MMIO resources, initializes the UART, autodetects receive polarity if needed, and registers rc-core. Open enables modem-status interrupts. The ISR reads UART status until no interrupt is pending, measures time between modem pin changes, filters spikes/noise through `frbwrite`, arms a timeout timer, and wakes raw decoding. TX iterates alternating pulse/space durations, toggling UART control pins or sending IRdeo serial bytes while maintaining target edge timing.

State and persistence: global module parameters define hardware type, I/O base, IRQ, mapped I/O, polarity, shared IRQ, and carrier behavior. Runtime state is global single-device state in `serial_ir`; no persistent storage exists. UART registers are reinitialized after resume.

Dependencies and integration points: depends on UART register definitions, port/MMIO I/O helpers, platform bus, interrupts, timers, rc-core raw RX/TX, and optional `CONFIG_IR_SERIAL_TRANSMITTER`. It often conflicts with the normal serial driver unless the port is reserved for IR.

Risks and edge cases: single global state prevents multiple instances. Busy-wait loops in TX and IRdeo send paths can burn CPU and depend on UART timing. IRQ handler has a pass limit but shared IRQ false positives are possible. Polarity autodetection can be wrong with noisy receivers. Resource acquisition requests IRQ before reserving port region. Softcarrier timing uses `ndelay`/`udelay` and can be imprecise under scheduling latency.

Test signals: loading with each hardware type, port existence test, active-high/low autodetection, raw pulse capture from a known remote, timeout event generation, TX waveform validation for homebrew/IRdeo, shared IRQ behavior, suspend/resume, and coexistence checks with disabled serial console/8250 ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/serial_ir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/st_rc.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/st_rc.c

Purpose: platform raw IR/UHF receiver driver for STMicroelectronics communication IRB hardware. It converts hardware mark and symbol-period FIFO values into standard rc-core pulse/space raw events.

Important APIs and functions: `struct st_rc_device` stores device, IRQ/wake state, clock, MMIO bases, rc device, overclock correction factors, UHF mode, and reset control. Main functions are `st_rc_hardware_init`, `st_rc_rx_interrupt`, `st_rc_send_lirc_timeout`, `st_rc_open`, `st_rc_close`, `st_rc_probe`, `st_rc_remove`, and PM suspend/resume handlers.

Control flow: probe requires DT `rx-mode` of `uhf` or `infrared`, obtains clock/reset/MMIO/IRQ resources, initializes hardware, registers a raw rc device, requests IRQ, enables wake IRQ, and sends an initial timeout for LIRC synchronization. Open enables RX interrupts and receiver; close disables them. The ISR drains FIFO/status for up to about 10 ms, handles overrun by reporting overflow and clearing status, reads symbol and mark, computes space as symbol minus mark, applies clock correction if needed, stores pulse and space events, and emits a timeout for the last symbol.

State and persistence: runtime state is in `st_rc_device` and volatile IRB registers. Clock divisor and max-symbol-period settings are reprogrammed on resume when not using wake-only suspend. No persistent storage exists.

Dependencies and integration points: depends on platform/OF, clocks, reset controls, pinctrl PM states, wakeirq helpers, MMIO, interrupts, and rc-core raw decoding. It integrates with system wake through `device_init_wakeup` and `dev_pm_set_wake_irq`.

Risks and edge cases: probe fails if `rx-mode` is absent or unexpected. Overclock correction uses integer scaling and may skew durations. The ISR ignores marks <=2 or symbols <=1 as noise and drains only until a jiffies timeout, so bursts under heavy interrupt load may leave FIFO data. Suspend wake path leaves hardware configured differently from full suspend. Remove disables the clock but does not assert reset.

Test signals: DT probe for IR and UHF modes, clock divisor correctness, IRQ FIFO drain under remote input, overrun handling, LIRC initial timeout, wake-from-suspend behavior, pinctrl sleep/default transitions, and raw decoder output against known protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/st_rc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/streamzap.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/streamzap.c

Purpose: USB raw IR receiver driver for Streamzap remotes. It decodes compact interrupt-URB bytes into pulse/space durations and feeds rc-core raw decoders.

Important APIs and functions: `struct streamzap_ir` stores rc device, USB interrupt URB, coherent input buffer, decoder state, and physical path. Decoder helpers include `sz_push*` and `sz_process_ir_data`; USB flow uses `streamzap_callback`, `streamzap_init_rc_dev`, `streamzap_probe`, `streamzap_disconnect`, `streamzap_suspend`, and `streamzap_resume`.

Control flow: probe validates a single interrupt IN endpoint, allocates coherent buffer and URB, registers a raw rc device with `RC_MAP_STREAMZAP`, fills the interrupt URB, and submits it. Completion decodes each byte with a small state machine handling half/full pulse and space encodings plus timeout marker `0xff`, stores filtered raw events, wakes decoding, and resubmits the URB. Suspend kills the URB; resume submits it again.

State and persistence: per-device state includes decoder state and USB buffers/URB. The rc device timeout is set to the hardware timeout duration. No persistent state exists beyond USB binding lifetime.

Dependencies and integration points: depends on USB input helpers, coherent DMA buffers, rc-core raw APIs, and the Streamzap keymap. It integrates with LIRC/raw decoders through `ir_raw_event_store_with_filter`.

Risks and edge cases: timeout is fixed by hardware and not exposed as a runtime timeout setter. URB resubmission errors in the callback are ignored. Error path after failed initial URB submit calls `rc_free_device` without `rc_unregister_device` even though registration succeeded, which is a cleanup path worth reviewing. The decoder state machine assumes byte stream continuity across URBs.

Test signals: USB probe endpoint validation, interrupt URB resubmission under remote input, decoding known Streamzap signals, timeout marker handling, suspend/resume, unplug while URB active, and keymap events through `RC_MAP_STREAMZAP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/streamzap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/sunxi-cir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/sunxi-cir.c

Purpose: platform raw IR receiver driver for Allwinner sunXi CIR controllers. It configures clocks/resets, reads RX FIFO bytes, converts them to pulse/space durations, and registers an rc-core raw receiver.

Important APIs and functions: `struct sunxi_ir_quirks` captures reset and FIFO-size differences; `struct sunxi_ir` stores rc device, MMIO base, IRQ, clocks, reset, and keymap. Main functions are `sunxi_ir_irq`, timeout conversion helpers, `sunxi_ir_set_timeout`, `sunxi_ir_hw_init`, `sunxi_ir_hw_exit`, probe/remove/shutdown, and PM suspend/resume.

Control flow: probe selects SoC quirks from OF match data, obtains APB and IR clocks, optional reset, sets IR base clock, maps registers, allocates/registers raw rc device, requests IRQ, then initializes hardware. Hardware init deasserts reset, enables clocks, selects CIR mode, programs noise and idle thresholds, inverts input, clears status, enables overflow/packet-end/FIFO interrupts, and enables RX. IRQ reads status, clears pending bits, drains available FIFO bytes up to FIFO size, stores filtered raw events, reports overflow or idle packet end, and wakes raw decoding.

State and persistence: per-device state is devm-managed except the rc device, which is explicitly unregistered/freed. Hardware register state is volatile and reinitialized after resume. Optional DT keymap name is stored as a pointer to DT property memory.

Dependencies and integration points: depends on OF, clocks, reset controls, platform MMIO/IRQ, and rc-core raw APIs. Device compatibles cover sun4i-a10, sun5i-a13, and sun6i-a31 variants.

Risks and edge cases: remove calls `rc_unregister_device` before `sunxi_ir_hw_exit`, so IRQs must be quiesced by managed IRQ teardown/order. Timeout conversion must avoid values outside 8-bit idle threshold; min/max are derived for sysfs validation. FIFO count macro depends on local `ir` variable, which is fragile style. Resume always reinitializes hardware regardless of users count.

Test signals: DT probe for each compatible, clock-rate programming, idle-threshold min/max behavior, FIFO drain under known remotes, overflow and packet-end handling, suspend/resume, shutdown clock/reset cleanup, and custom `linux,rc-map-name`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/sunxi-cir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ttusbir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ttusbir.c

Purpose: USB raw IR receiver driver for TechnoTrend TT USB IR hardware. It consumes high-rate isochronous sample packets, converts one-bit samples to raw events, and controls the device LED through a bulk endpoint.

Important APIs and functions: `struct ttusbir` stores rc device, USB device, four isochronous URBs, LED classdev, LED bulk URB/buffer, endpoints, LED state, and physical path. Main functions are LED callbacks, `ttusbir_process_ir_data`, `ttusbir_urb_complete`, `ttusbir_probe`, disconnect, suspend, and resume.

Control flow: probe searches alternate settings for an isochronous IN endpoint with 0x10 max packet and a bulk OUT endpoint with 0x20 max packet, sets that interface, allocates four 8-frame isochronous URBs with 128-byte coherent buffers, allocates a LED bulk URB, registers LED and raw rc device, then submits all URBs. Each isochronous completion decodes 128 bytes where set bits mean silence, handles full-byte pulse/space and single-edge cases, filters raw events, wakes decoders only when data changed, and resubmits the URB. LED writes submit a serialized bulk URB when requested state differs.

State and persistence: per-device state includes URBs, coherent buffers, LED pending flag, and rc settings. Runtime state is volatile; disconnect kills URBs, unregisters rc/LED, frees buffers, and clears interface data.

Dependencies and integration points: depends on USB isochronous/bulk APIs, LED class, rc-core raw decoding, and keymap `RC_MAP_TT_1500`.

Risks and edge cases: the probe allocation check is suspicious: `if (!tt || !rc || buffer)` treats successful `buffer` allocation as an error, so this snapshot appears to fail normal probe before assigning `tt->bulk_buffer`. If fixed, high-rate idle URBs still require efficient filtering to avoid unnecessary decoder wakeups. LED state uses atomic serialization but relies on barriers and `udev` nulling during disconnect. Resume returns the last submit status and stops after first URB failure.

Test signals: build/static analysis should catch the probe condition, USB probe after correcting allocation logic, alternate-setting selection, sustained isochronous input, raw timing accuracy around one-edge bytes, LED trigger behavior, suspend/resume URB restart, and disconnect races with LED bulk completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ttusbir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/winbond-cir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/winbond-cir.c

Purpose: PNP driver for Winbond WPCD376I consumer IR hardware. It supports raw IR receive, transmit, carrier reporting, LED feedback, and shutdown/suspend wake-on-CIR matching for NEC/RC5/RC6-family protocols.

Important APIs and functions: `struct wbcir_data` stores resource bases, IRQ mask, rc device, LED, RX/TX state, carrier-report state, TX buffer/cursor/mask/carrier, and lock. Major functions include bank/register helpers, `wbcir_irq_handler`, RX/TX interrupt handlers, `wbcir_idle_rx`, carrier report, TX carrier/mask/send callbacks, wake pattern `wbcir_shutdown`, `wbcir_init_hw`, PNP probe/remove, and suspend/resume.

Control flow: probe validates three PNP I/O regions and IRQ, registers LED and raw rc device, claims regions/IRQ, enables wake, and initializes hardware. RX IRQ drains run-length encoded FIFO bytes into raw pulse/space events and tracks pulse duration for carrier reports. TX converts durations to 10 us units and fills the hardware FIFO incrementally from interrupt context until end-of-transmission. Shutdown/suspend translates the configured wake scancode and mask into hardware compare/mask bytes, enables CEIR wake matching when valid, then disables runtime IRQs.

State and persistence: volatile driver state is in `wbcir_data`; hardware register state spans wake, enhanced, and serial-port register banks. Wake filter settings live in `rc_dev` and are programmed into wake registers on shutdown/suspend; they are not stored on disk.

Dependencies and integration points: depends on PNP resources, port I/O, IRQs, LED class, bit reversal helpers, rc-core raw RX/TX, and rc-core wake filter sysfs. Default keymap is `RC_MAP_RC6_MCE`.

Risks and edge cases: `wbcir_irq_tx` contains a duplicated `kfree(data->txbuf)` in this snapshot, which is a serious double-free risk when transmission finishes. `wbcir_suspend` has a duplicate `return 0`, harmless but untidy. Wake RC6_6A_20 appears referenced inside a case group that does not include it, making that branch unreachable. TX/RX sharing depends on `txandrx` and interrupt masking; changing it can cause underruns or RX loss. Direct port I/O requires exact PNP resources.

Test signals: PNP probe on WEC1022, RX event decoding, carrier report accuracy, TX send completion and underrun handling, KASAN/slab validation for TX completion double-free, LED feedback, wake filter programming for NEC/RC5/RC6, suspend/resume, shutdown wake from S-state, and remove cleanup of regions/IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/winbond-cir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/xbox_remote.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/xbox_remote.c

Purpose: USB scancode rc-core driver for original Xbox DVD Movie Playback Kit IR dongles from Microsoft and Gamester. It reads interrupt reports and emits `RC_PROTO_XBOX_DVD` scancodes through rc-core.

Important APIs and functions: `struct xbox_remote` stores rc device, USB device/interface, interrupt URB, input buffer, and name/path strings. Key functions are `xbox_remote_rc_open`, `xbox_remote_rc_close`, `xbox_remote_input_report`, `xbox_remote_irq_in`, `xbox_remote_rc_init`, `xbox_remote_initialize`, probe, and disconnect.

Control flow: probe validates a single interrupt IN endpoint, allocates state, scancode rc device, buffer, and URB, builds device name/path, sets default keymap `RC_MAP_XBOX_DVD`, initializes rc fields, fills the interrupt URB, and registers rc-core. The URB is submitted on rc device open and killed on close. Completion validates six-byte reports, extracts a little-endian 16-bit key code from bytes 2-3, calls `rc_keydown`, and resubmits the URB.

State and persistence: per-device USB and rc state lives until disconnect. Last-key/repeat timing is handled by rc-core using a 10 ms timeout. No persistent storage exists.

Dependencies and integration points: depends on USB interrupt APIs, USB input ID helpers, rc-core scancode mode, protocol `RC_PROTO_XBOX_DVD`, and keymap `RC_MAP_XBOX_DVD`.

Risks and edge cases: the report validation uses `urb->actual_length != 6 || urb->actual_length != data[1]`, so any mismatch logs and drops input. There is no suspend/resume handler; open URBs rely on USB core disconnect/reset behavior. Unaligned cast to `__le16 *` on `data + 2` is typically safe on supported architectures but less robust than `get_unaligned_le16`. A zero-endpoint alternate interface is silently ignored.

Test signals: USB probe for both vendor/product IDs, open/close URB submission, six-byte report decoding, keymap events, repeat/keyup timing with 10 ms timeout, unplug while opened, malformed report logging, and behavior across USB reset/suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/xbox_remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/spi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/spi/Kconfig

Purpose: defines Kconfig menu entries for media SPI adapter drivers, currently Sony CXD2880 SPI support and Gennum GS1662 serializer support.

Important APIs and symbols: the file is gated by `if VIDEO_DEV && SPI`. `CXD2880_SPI_DRV` is a tristate depending on `DVB_CORE && SPI` and defaults to module when ancillary autoselect is disabled. `VIDEO_GS1662` is a tristate depending on `SPI && VIDEO_DEV`, selecting `MEDIA_CONTROLLER` and `VIDEO_V4L2_SUBDEV_API`.

Control flow: Kconfig selection controls whether the matching Makefile builds `cxd2880-spi.o` and/or `gs1662.o`. The top comment for hidden ancillary subdrivers informs menu visibility when `MEDIA_HIDE_ANCILLARY_SUBDRV` is active.

State and persistence: selected values persist only in the kernel build configuration. There is no runtime state.

Dependencies and integration points: integrates with the media driver Kconfig hierarchy, DVB core, SPI core, V4L2 device support, media controller, and ancillary-driver autoselection policy.

Risks and edge cases: the outer `VIDEO_DEV && SPI` gate means CXD2880 SPI support is hidden if `VIDEO_DEV` is off even though the symbol itself depends on DVB core and SPI. Default module behavior changes with `MEDIA_SUBDRV_AUTOSELECT`, so build coverage should include both manual and autoselected configurations.

Test signals: `menuconfig` visibility, `allyesconfig/allmodconfig` builds, configs with `MEDIA_SUBDRV_AUTOSELECT` enabled/disabled, and module presence for `cxd2880-spi` and `gs1662`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/spi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/spi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/spi/Makefile

Purpose: kbuild file mapping media SPI Kconfig symbols to object files.

Important APIs and entries: it adds the CXD2880 frontend include directory with `ccflags-y += -I $(srctree)/drivers/media/dvb-frontends/cxd2880`. It builds `cxd2880-spi.o` for `CONFIG_CXD2880_SPI_DRV` and `gs1662.o` for `CONFIG_VIDEO_GS1662`.

Control flow: during kernel builds, selected config symbols append the corresponding object to the directory target. The comment asks maintainers to keep entries sorted by Kconfig name.

State and persistence: no runtime state. Build outputs are determined by `.config`.

Dependencies and integration points: integrates `drivers/media/spi` with the CXD2880 DVB frontend headers and kbuild symbol expansion from the sibling Kconfig file.

Risks and edge cases: adding new CXD2880 include paths or source splits requires keeping the include flag and object mapping in sync. Sort-order comments are maintenance-only and not enforced.

Test signals: compile with each config enabled independently and together; verify CXD2880 headers resolve and module names match Kconfig help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/spi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/spi/cxd2880-spi.c -->
# sources/distributed-fs/ceph-client/drivers/media/spi/cxd2880-spi.c

Purpose: SPI adapter and DVB glue for the Sony CXD2880 DVB-T2/T tuner/demodulator. It powers the chip, attaches the CXD2880 frontend, registers DVB adapter/frontend/demux devices, manages PID filtering, and runs a kernel thread to pull MPEG-TS packets over SPI.

Important APIs and functions: `struct cxd2880_dvb_spi` owns DVB frontend/adapter/demux/dmxdev/frontend, SPI device, mutex, feed counters, optional regulator, TS buffer, and PID filter config. SPI helpers include `cxd2880_write_spi`, `cxd2880_write_reg`, `cxd2880_spi_read_ts`, `cxd2880_spi_read_ts_buffer_info`, and `cxd2880_spi_clear_ts_buffer`. DVB feed callbacks are `cxd2880_start_feed` and `cxd2880_stop_feed`; lifecycle is `cxd2880_spi_probe` and `cxd2880_spi_remove`.

Control flow: probe allocates state, optionally enables `vcc`, sets SPI drvdata and mutex, registers a DVB adapter, attaches/registers the frontend, initializes demux and dmxdev, adds/connects a hardware frontend, then leaves feeds idle. Starting the first feed allocates a DMA-capable TS buffer and starts `cxd2880_ts_read`; PID feeds update the 32-entry hardware filter unless all-PID feed `0x2000` is active. The read thread clears the TS buffer, polls buffer info, reads large batches immediately or smaller batches after 500 ms, and passes TS bytes to `dvb_dmx_swfilter`. Stopping the last feed stops the thread and frees the TS buffer.

State and persistence: runtime state tracks feed counts, all-PID count, PID filter table, read thread, regulator state, and transient TS buffer. Hardware PID filter and TS buffer state are volatile. No persistent storage exists.

Dependencies and integration points: depends on SPI core, optional regulator framework, DVB adapter/frontend/demux/dmxdev APIs, the CXD2880 frontend attach function and config, kthreads, mutexes, and OF/SPI device IDs.

Risks and edge cases: feed_count/filter updates are not protected by a dedicated mutex, so concurrent DVB feed start/stop calls could race. `cxd2880_spi_read_ts_buffer_info` fills `info` even when `spi_write_then_read` fails, using possibly stale stack data. The read thread returns on SPI errors; subsequent stop may see a nonzero `kthread_stop` result. Remove does not explicitly stop active feeds before tearing down DVB structures, relying on DVB core shutdown ordering. Large `pkt_num` is split by integer division, leaving a remainder for later polling.

Test signals: SPI probe with and without `vcc`, frontend attach and tuning, DVB demux open/close, PID filter updates for normal and all-PID feeds, TS packet continuity under high bitrate, SPI error injection, concurrent feed start/stop stress, remove while feeds are active, and regulator disable on probe/remove failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/spi/cxd2880-spi.c -->
