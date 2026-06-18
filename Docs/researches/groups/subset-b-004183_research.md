# subset-b-004183 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-hw.c

Purpose: implements the ImgTec PowerDown Controller IR hardware-decoder side of rc-core integration. It consumes protocol descriptors from the sibling `img-ir-*.c` modules, converts their abstract pulse/space timings into register values, registers a `RC_DRIVER_SCANCODE` device, handles decoded-data interrupts, supports normal and wakeup scancode filters, and maintains repeat-mode timing for protocols with compact repeat frames.

Important APIs, types, and functions: the central state is `struct img_ir_priv_hw` from `img-ir-hw.h`, reached through `struct img_ir_priv`. The static `img_ir_decoders[]` table is compiled from enabled protocol modules. Timing helpers include `img_ir_timing_preprocess()`, `img_ir_timings_convert()`, `img_ir_decoder_preprocess()`, and `img_ir_decoder_convert()`. Hardware programming helpers include `img_ir_control()`, `img_ir_write_timings()`, `img_ir_write_filter()`, `_img_ir_set_filter()`, and `_img_ir_set_wake_filter()`. rc-core callbacks are `img_ir_change_protocol()`, `img_ir_set_normal_filter()`, and `img_ir_set_wakeup_filter()`. Runtime entry points exported to the core driver are `img_ir_isr_hw()`, `img_ir_setup_hw()`, `img_ir_probe_hw()`, `img_ir_remove_hw()`, `img_ir_suspend()`, and `img_ir_resume()`.

Control flow: probe preprocesses the global decoder descriptors once under `img_ir_decoders_lock`, records hardware quirks, initializes repeat and quirk timers, samples the IR clock or falls back to 32768 Hz, optionally registers a common-clock notifier, allocates an rc-core scancode device, registers it, and enables device wakeup. Setup selects the first compatible decoder and writes protocol timings/control registers. User protocol changes call `img_ir_change_protocol()`, which chooses one compatible decoder from the requested bitmap and calls `img_ir_set_decoder()`. That function stops timers without holding the spinlock, disables decode/IRQs, drains status/data, clears filters and wake state, converts timings for the current clock, writes timing registers, and re-enables the hardware. Interrupts enter `img_ir_isr_hw()` with `priv->lock` already held by the core ISR; it checks decoder presence, handles the biphase spurious-IRQ quirk by disabling decode and scheduling `suspend_timer`, acknowledges valid data, adjusts quirked lengths, reads low/high data registers, and passes the raw frame to `img_ir_handle_data()`. `img_ir_handle_data()` calls the protocol-specific scancode hook, emits `rc_keydown()` or `rc_repeat()`, and manages repeat-mode timing through `end_timer`.

State and persistence behavior: persistent runtime state is kernel memory only. `hw->decoder`, `enabled_protocols`, `reg_timings`, `mode`, `flags`, and `filters[]` represent the active hardware configuration. `hw->mode` moves between normal, repeating, and wake modes; timer callbacks return the hardware to normal timings or recover from a quirk-induced temporary disable. Wake filters are stored separately from normal filters and copied into the hardware only during suspend. Clock-rate changes recompute timing register values and rewrite the active timing set while preserving mode.

Dependencies and integration points: depends on rc-core for device registration, protocol bitmaps, scancode filters, `rc_keydown()`, and `rc_repeat()`. It depends on the ImgTec register definitions and `img_ir_read()/img_ir_write()` from `img-ir.h`, protocol descriptors declared in `img-ir-hw.h`, common clock notifiers when available, timers, spinlocks, PM wake IRQs, and device wakeup support. It integrates with the unlisted `img-ir-core.c` through `img_ir_probe_hw()`, `img_ir_setup_hw()`, and `img_ir_isr_hw()`.

Risks and edge cases: timing conversion has rounding and tolerance-sensitive paths, so clock changes and protocol timing descriptors are high risk. `img_ir_set_decoder()` intentionally drops the spinlock around synchronous timer deletion; incorrect future changes could deadlock or race repeat rearming. Hardware quirks disable RC-MM-like two-bit pulse-position decode, increment pulse-length bit counts, and recover biphase interrupt storms; new silicon revisions need careful quirk validation. Filter handling changes IRQ sources between data-valid and data-match paths, so stale IRQ clearing and min/max length tightening are important. Wake mode rewrites filters/timings during suspend and must restore the exact normal IRQ/filter state on resume.

Test signals: exercise rc-core protocol selection through `ir-keytable`, filter and wakeup filter programming, NEC/Sanyo repeat frames, RC5/RC6 biphase data and quirk interrupt recovery, clock-rate changes if the clock provider supports them, suspend/resume wake by IR match, and module removal while timers/IRQs may be active. Useful kernel logs include timing register debug output, raw filter debug output, quirk recovery behavior, and rc-core keydown/repeat events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-hw.h

Purpose: defines the ImgTec hardware-decoder contract shared by the hardware driver and per-protocol descriptor modules. It describes hardware control fields, abstract protocol timings, raw match filters, scancode conversion callbacks, calculated timing registers, runtime hardware-decoder private state, and stubs used when `CONFIG_IR_IMG_HW` is disabled.

Important APIs, types, and functions: code-type constants classify pulse-length, pulse-distance, biphase, and two-bit pulse-position decoding. `struct img_ir_control` maps protocol control settings to the `IMG_IR_CONTROL` register. `struct img_ir_timing_range`, `img_ir_symbol_timing`, `img_ir_free_timing`, and `img_ir_timings` represent protocol timing windows before conversion. `struct img_ir_filter` models hardware data/mask plus length restrictions. `struct img_ir_scancode_req` is filled by decoder-specific `scancode()` callbacks. `struct img_ir_decoder` is the core protocol descriptor: protocol bitmap, tolerance, unit scaling, primary/repeat timings, repeat interval, control bits, scancode hook, and filter hook. `struct img_ir_priv_hw` stores runtime rc-core device, timers, active decoder, converted timings, filters, and suspend/quirk state.

Control flow: protocol modules instantiate external `img_ir_decoder` objects declared here. `img-ir-hw.c` preprocesses those objects, converts timings, writes registers, and dispatches decoded raw frames through the callbacks. Core driver code calls the declared `img_ir_probe_hw()`, `img_ir_setup_hw()`, `img_ir_isr_hw()`, and `img_ir_remove_hw()` functions when hardware decoding is enabled; otherwise static stubs compile away the feature and report disabled state.

State and persistence behavior: this header itself has no storage, but it defines all durable in-memory hardware decoder state. `img_ir_priv_hw` persists for the platform device lifetime and tracks active protocol, converted register values for the current clock, normal and wake filters, mode, stopping flag, and saved IRQ masks. No userspace-visible persistent storage is defined here.

Dependencies and integration points: includes `media/rc-core.h` for protocol enums, filter types, and `struct rc_dev` semantics. It forward-declares `struct img_ir_priv` to avoid cycles with `img-ir.h`. It is consumed by `img-ir-hw.c` and by `img-ir-nec.c`, `img-ir-jvc.c`, `img-ir-sony.c`, `img-ir-sharp.c`, `img-ir-sanyo.c`, `img-ir-rc5.c`, and `img-ir-rc6.c`.

Risks and edge cases: bitfield layout in `struct img_ir_control` is used as logical fields only, not as an MMIO overlay; callers must keep conversion logic centralized. `filter` callbacks can be absent or return `-EINVAL`, which disables wake filter support for those protocols. Stub behavior returns `-ENODEV` when disabled, so callers must tolerate mixed raw-only or hardware-only builds.

Test signals: build coverage should include `CONFIG_IR_IMG_HW=y` and disabled configurations. Runtime tests should confirm exported protocol descriptors link, `img_ir_hw_enabled()` reflects `rdev` presence, and PM entry points resolve to real functions only under sleep PM plus hardware decoder support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-jvc.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-jvc.c

Purpose: provides the ImgTec hardware-decoder descriptor for the JVC pulse-distance IR protocol. It translates 16-bit hardware-decoded raw frames into rc-core JVC scancodes and converts rc-core scancode filters into ImgTec hardware data/mask filters.

Important APIs, types, and functions: `img_ir_jvc_scancode()` validates `len == 16`, extracts customer and data bytes from raw `cust | data << 8`, sets `RC_PROTO_JVC`, and returns `IMG_IR_SCANCODE`. `img_ir_jvc_filter()` maps scancode `cust:data` into the hardware raw order and mask. The exported `struct img_ir_decoder img_ir_jvc` declares `RC_PROTO_BIT_JVC`, pulse-distance code type, 527.5 us units, leader/zero/one timings, fixed 16-bit length, and the two callbacks.

Control flow: `img-ir-hw.c` includes this descriptor in its decoder list when `CONFIG_IR_IMG_JVC` is enabled. During protocol selection, the hardware layer writes the descriptor's timings and control fields. At interrupt time the raw frame is routed to `img_ir_jvc_scancode()`, which emits a scancode through the generic hardware handler.

State and persistence behavior: the file has no mutable persistent state. The descriptor is static module data; runtime state is held in the parent hardware decoder.

Dependencies and integration points: depends on `img-ir-hw.h` for descriptor types and rc-core protocol constants. It integrates with rc-core only indirectly through the hardware driver. It mirrors the software JVC decoder's bit layout but avoids raw pulse parsing because the ImgTec hardware already classified symbols.

Risks and edge cases: only exact 16-bit frames are accepted. Filter translation assumes the JVC scancode layout used by rc-core and the raw byte order expected by the hardware; regressions here would cause wake/filter mismatches while unfiltered receive still works. Repeat semantics are not modeled in this descriptor, so JVC repeat behavior depends on hardware-visible data frames rather than a dedicated no-data repeat path.

Test signals: enable the hardware decoder, select JVC with `ir-keytable`, verify a known JVC remote produces `RC_PROTO_JVC` scancodes, and set normal/wakeup scancode filters to confirm data/mask order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-jvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-nec.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-nec.c

Purpose: provides the ImgTec hardware-decoder descriptor for NEC-family IR protocols: normal NEC, extended NEC, and NEC32. It maps hardware-decoded raw fields to rc-core protocol-specific scancodes and supports hardware scancode filtering for all NEC variants.

Important APIs, types, and functions: `img_ir_nec_scancode()` treats zero-length frames as repeat codes, requires 32 data bits otherwise, extracts raw `ddDDaaAA`, distinguishes NEC32 when the command inverse check fails, NECX when the address inverse check fails, and normal NEC when both inverse checks match. It uses `bitrev8()` for NEC32's transmitted-order scancode encoding. `img_ir_nec_filter()` chooses an exact protocol from the supplied protocol bitmap or infers one from the scancode/mask, then builds raw data/mask in the hardware order. The exported `img_ir_nec` descriptor declares pulse-distance timing, 562.5 us units, NEC leader and bit timings, fixed 32-bit normal length, 108 ms repeat interval, and repeat timing with zero data bits.

Control flow: the parent hardware layer preprocesses and converts the descriptor, then calls `img_ir_nec_scancode()` for decoded frames. A zero-length repeat frame returns `IMG_IR_REPEATCODE`, causing the hardware layer to call `rc_repeat()` only while it is already in repeating mode. Filter programming calls `img_ir_nec_filter()` from rc-core normal or wake filter callbacks.

State and persistence behavior: no mutable state is stored here. NEC repeat behavior is encoded in descriptor fields and managed by `img-ir-hw.c` timers.

Dependencies and integration points: uses `linux/bitrev.h`, `linux/log2.h` for `is_power_of_2()`, and `img-ir-hw.h`. Integrates with rc-core NEC protocol bitmaps and wake filtering through the hardware driver.

Risks and edge cases: protocol inference from scancode and mask matters for normal filters; wake filters should pass one exact protocol bit. Incorrect inverse handling would misclassify NECX versus NEC32. Zero-length repeat frames depend on the parent repeat-mode timer and may be ignored if received before a primary scancode.

Test signals: test normal NEC, NECX, and NEC32 scancodes, verify repeat frames generate rc repeats after an initial keydown, and verify scancode filters for each variant, especially NEC32 bit-reversal cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-nec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-raw.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-raw.c

Purpose: implements the raw-edge ImgTec IR receive path for systems that use generic software raw decoders instead of the ImgTec hardware scancode decoder. It registers a `RC_DRIVER_IR_RAW` rc-core device, enables edge interrupts, converts hardware level changes into raw edge events, and emits a final echo sample after quiet periods.

Important APIs, types, and functions: `img_ir_refresh_raw()` reads `IMG_IR_STATUS`, filters same-level double-edge noise, stores rising/falling edges with `ir_raw_event_store_edge()`, and calls `ir_raw_event_handle()`. `img_ir_isr_raw()` is called by the core ISR with the device spinlock held; it refreshes raw state and pushes the echo timer. `img_ir_echo_timer()` emits a final sample when no edges arrive for `ECHO_TIMEOUT_MS`. `img_ir_setup_raw()` enables `IMG_IR_IRQ_EDGE`. `img_ir_probe_raw()` allocates and registers the raw rc-core device. `img_ir_remove_raw()` unregisters the device, disables edge IRQs, clears pending edge IRQs, frees the rc device, and deletes the timer.

Control flow: probe creates the rc-core raw device and timer. Setup enables edge interrupts after the platform device has been initialized. Each edge interrupt refreshes the raw decoder state and schedules the echo timer. The echo timer reacquires `priv->lock` and refreshes with `irq_status == 0`, which bypasses double-edge treatment while preserving the final-space signal expected by raw decoders.

State and persistence behavior: `struct img_ir_priv_raw` stores the rc device pointer, timer, and last sampled level. `raw->rdev` is also the enabled/removing guard; removal sets it to `NULL` under `priv->lock` before deleting the timer. There is no persistent storage beyond device lifetime.

Dependencies and integration points: depends on `img-ir.h` register definitions and `media/rc-core.h` raw event APIs. It shares `priv->lock` and IRQ status dispatch with the platform core and can coexist with the hardware decoder depending on build/configuration.

Risks and edge cases: double-edge interrupts can be noise if the sampled level did not change; the filter avoids false raw transitions. Timer deletion order matters during removal because the timer also takes `priv->lock`. The final echo sample is necessary for decoders that need an ending space; removing it may break software protocol decoders despite correct edges.

Test signals: with raw mode enabled, use a known remote and verify generic software decoders receive events. Test quiet-period completion for protocols with long trailer spaces, removal while IR activity is present, and simultaneous rise/fall IRQ status noise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-raw.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-raw.h

Purpose: declares the ImgTec raw-decoder private state and entry points, with build-time stubs for configurations without raw ImgTec IR support.

Important APIs, types, and functions: `struct img_ir_priv_raw` contains the raw `rc_dev`, echo `timer_list`, and last sampled status. `img_ir_raw_enabled()` returns whether a raw rc-core device is active. The declared implementation hooks are `img_ir_isr_raw()`, `img_ir_setup_raw()`, `img_ir_probe_raw()`, and `img_ir_remove_raw()`. The disabled stubs return false or no-op, with probe returning `-ENODEV`.

Control flow: `img-ir.h` embeds `struct img_ir_priv_raw` inside the platform private data. The core driver can call the raw hooks unconditionally; this header makes those calls compile out when `CONFIG_IR_IMG_RAW` is off.

State and persistence behavior: when enabled, state is runtime-only and bound to the platform device. When disabled, the struct is empty and no state exists.

Dependencies and integration points: forward-declares `struct img_ir_priv` to avoid including the full core header. It integrates with `img-ir-raw.c` and the unlisted platform core ISR/setup paths.

Risks and edge cases: callers should use `img_ir_raw_enabled()` or tolerate stubs. Probe returning `-ENODEV` is expected in disabled builds and should not be reported as a hardware failure unless raw support was required.

Test signals: compile both enabled and disabled configurations and verify the core driver builds without conditional call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-rc5.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-rc5.c

Purpose: provides the ImgTec hardware descriptor for Philips RC-5. It compensates for hardware bit shifting and emits rc-core RC5 scancodes with toggle state.

Important APIs, types, and functions: `img_ir_rc5_scancode()` shifts raw data right by two due to a hardware quirk, validates the start bit, extracts toggle, address, and six-bit command, extends the command with the RC5 field bit, sets `RC_PROTO_RC5`, and returns `IMG_IR_SCANCODE`. `img_ir_rc5_filter()` returns `-EINVAL` because this hardware path cannot support RC5 scancode filters. The exported `img_ir_rc5` descriptor uses biphase code type, secondary decoder (`decodend2`), MSB-first secondary bit orientation, 888.888 us units, 14-bit length, and 16 percent tolerance.

Control flow: the hardware layer selects this descriptor when RC5 is requested and compatible. Decoded frames are passed to the scancode callback; filters and wake filters are rejected because the descriptor's filter hook always fails.

State and persistence behavior: no local mutable state. Toggle handling is per-frame and repeat behavior is left to rc-core key repeat logic rather than a descriptor repeat frame.

Dependencies and integration points: depends on `img-ir-hw.h` and rc-core RC5 protocol constants. It is sensitive to the parent hardware's biphase interrupt quirk handling.

Risks and edge cases: hardware shift compensation is mandatory; removing it breaks every scancode. Filtering is unsupported, so wakeup protocol availability is suppressed by the parent when this decoder is active. Only standard RC5 is supported here, not RC5X or StreamZap variants handled by the software raw decoder.

Test signals: test known RC5 remotes, toggle-bit alternation, protocol selection rejection for wake filters, and biphase quirk recovery under partial/incomplete messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-rc5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-rc6.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-rc6.c

Purpose: provides a limited ImgTec hardware descriptor for RC6 mode 0. It reconstructs header/trailer information around known hardware decoder behavior and emits `RC_PROTO_RC6_0` scancodes.

Important APIs, types, and functions: `img_ir_rc6_scancode()` shifts raw data, extracts two trailer samples, mode, address, and command, validates that trailer samples differ, rejects nonzero modes, sets the scancode to `addr << 8 | cmd`, and uses `trl2` as toggle. `img_ir_rc6_filter()` returns `-EINVAL`. The exported `img_ir_rc6` descriptor uses biphase code type, active-high input, MSB-first orientation, explicit RTL-derived leader/bit timings, 20 percent tolerance, fixed 21-bit length, and no filter support.

Control flow: selected through the parent hardware decoder for `RC_PROTO_BIT_RC6_0`. The descriptor supplies custom timings because default RC6 header timings did not work with this hardware block. Decoded frames go through the scancode callback and then `rc_keydown()` in the parent.

State and persistence behavior: no mutable local state. Toggle is derived per message. Filter and wake state are not supported for RC6 on this hardware path.

Dependencies and integration points: depends on `img-ir-hw.h`; integrates with the parent hardware quirk that biphase decoding can produce interrupt storms after incomplete codes.

Risks and edge cases: only mode 0 is supported; RC6-6A/MCE variants are handled by the generic software decoder, not this hardware descriptor. Header recovery is explicitly a workaround for hardware side effects. Filters are unsupported, so userspace should not expect wake-filter matching.

Test signals: verify RC6-0 devices produce correct scancodes and toggles; verify RC6-MCE is not advertised by this hardware descriptor; test incomplete biphase frames for quirk timer recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-rc6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sanyo.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sanyo.c

Purpose: provides the ImgTec hardware-decoder descriptor for Sanyo/Aiwa/Chinon style IR, a NEC-timed protocol with 13-bit address and inverted address plus 8-bit command and inverted command.

Important APIs, types, and functions: `img_ir_sanyo_scancode()` treats zero-length frames as repeat codes, requires 42 data bits, extracts address, inverted address, command, and inverted command, validates both inversion checks, and emits `RC_PROTO_SANYO` with `addr << 8 | data`. `img_ir_sanyo_filter()` rejects out-of-range scancodes, constructs raw data/mask including inverted fields, and supports hardware filtering. The exported `img_ir_sanyo` descriptor uses pulse-distance timings matching NEC, 562.5 us units, 42-bit fixed length, 108 ms repeat interval, and zero-length repeat timings.

Control flow: the parent hardware decoder writes Sanyo timing registers and calls the scancode function for data frames. Repeat frames are routed as `IMG_IR_REPEATCODE` and handled by the parent's repeat state. Filters are converted to raw data/mask by `img_ir_sanyo_filter()`.

State and persistence behavior: no local mutable state. Repeat-mode state is descriptor-driven and stored in `img-ir-hw.c`.

Dependencies and integration points: depends on `img-ir-hw.h` and rc-core Sanyo protocol constants. It shares NEC-like timing expectations with both the software Sanyo decoder and NEC descriptor.

Risks and edge cases: address and command inverse validation must match the protocol; otherwise noise could become key events. Filter masks duplicate data masks across inverted command fields and address masks across inverted address fields, so partial filters need careful validation. Out-of-range high address bits are rejected.

Test signals: test full 42-bit Sanyo frames, invalid inverse fields, repeat frames after keydown, and wake/normal filters for address-only and address+command masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sanyo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sharp.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sharp.c

Purpose: provides the ImgTec hardware descriptor for Sharp IR. It decodes the first half of Sharp-style messages and supports command-aware hardware filtering.

Important APIs, types, and functions: `img_ir_sharp_scancode()` requires 15 bits, extracts address, command, expansion bit, and check bit, rejects messages without the expansion bit or with the check bit set because those are likely the second half of the paired message, and emits `RC_PROTO_SHARP`. `img_ir_sharp_filter()` maps address/command filters to raw bits and, when command filtering is requested, constrains `exp=1` and `chk=0` to match only the first part. The `img_ir_sharp` descriptor uses pulse-distance code type, secondary decoder mode (`decodend2`), `d1validsel`, 20 percent tolerance, 320 us pulse with 680/1680 us spaces, fixed 15-bit length, and filter support.

Control flow: selected by the parent hardware decoder for `RC_PROTO_BIT_SHARP`. The hardware decodes secondary no-leader symbols; the scancode callback filters out second-half echoes, then the parent emits keydown.

State and persistence behavior: no mutable state. The two-part Sharp message protocol is handled by rejecting the second half rather than storing pairing state.

Dependencies and integration points: depends on `img-ir-hw.h`. It mirrors the software Sharp decoder's first/second frame rules but relies on hardware symbol decoding.

Risks and edge cases: rejecting second halves avoids duplicate keydown but assumes the first half is always available and sufficient. Filter behavior changes when command mask is nonzero, so address-only filters are less constrained than command filters. No repeat descriptor is present.

Test signals: test known Sharp remotes, first/second half suppression, address-only and address+command filters, and no-leader secondary decoder timing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sharp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sony.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sony.c

Purpose: provides the ImgTec hardware descriptor for Sony SIRC 12-, 15-, and 20-bit variants. It converts variable-length hardware data into rc-core Sony scancodes and builds length-constrained hardware filters.

Important APIs, types, and functions: `img_ir_sony_scancode()` switches on decoded bit length, checks the enabled protocol bitmap, extracts function, device, and optional subdevice fields, sets the appropriate `RC_PROTO_SONY12`, `RC_PROTO_SONY15`, or `RC_PROTO_SONY20`, and emits `dev << 16 | subdev << 8 | func`. `img_ir_sony_filter()` extracts scancode fields and masks, chooses or infers a Sony variant, validates 20-bit device limits, handles the hardware ambiguity between high device bits and low extended bits, writes raw data/mask, and optionally sets `out->minlen/maxlen`. The descriptor uses pulse-length code type, 600 us units, Sony leader and pulse-length bit timings, and 12-20 bit length range.

Control flow: the parent hardware decoder may enable a subset of Sony variants. When raw frames arrive, the scancode callback rejects lengths not included in the currently enabled protocol bitmap. Filter conversion either honors one exact protocol bit or infers a length from masked scancode fields.

State and persistence behavior: no mutable local state. Length restrictions for filters are returned through `struct img_ir_filter` and then tightened into the free-time register by the parent.

Dependencies and integration points: depends on `img-ir-hw.h` and rc-core Sony protocol bitmaps. The parent has a pulse-length bit-count increment quirk for this code type.

Risks and edge cases: filter inference can be ambiguous for Sony12 high device bits versus Sony20 subdevice bits, and the code explicitly ANDs masks to represent hardware limitations. The pulse-length quirk in the parent affects reported lengths. Userspace wake filters should pass an exact protocol to avoid inference surprises.

Test signals: test all Sony12/15/20 variants, enabled-protocol subsets, filter length restriction, high device-bit ambiguity, and wake filters for each exact variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sony.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir.h

Purpose: central private header for the ImgTec IR platform driver. It defines the MMIO register map and bit masks for the PowerDown Controller IR block, composes raw and hardware decoder private state into `struct img_ir_priv`, and provides inline MMIO accessors.

Important APIs, types, and functions: register offsets include control, status, data low/high, symbol timing registers, power modulation registers, interrupt message filters, IRQ enable/status/clear, and core identification/revision registers. Bit masks define control fields, status validity/length/level bits, symbol timing field packing, free-time length fields, power modulation fields, IRQ sources, and core ID/revision fields. `struct img_ir_priv` stores the platform device, IRQ, input clocks, MMIO base, spinlock, `raw` decoder state, and `hw` decoder state. `img_ir_write()` and `img_ir_read()` wrap `iowrite32()` and `ioread32()`.

Control flow: `img-ir-core.c` uses this header to initialize the platform device and dispatch IRQs. `img-ir-raw.c` and `img-ir-hw.c` use the register constants and accessors to program or sample the hardware. The private struct is the shared state object passed through all ImgTec IR submodules.

State and persistence behavior: defines runtime state only. `reg_base` anchors all register access; `lock` serializes register and private-state manipulation across interrupt, timer, PM, and userspace protocol/filter paths.

Dependencies and integration points: includes Linux I/O and spinlock APIs plus `img-ir-raw.h` and `img-ir-hw.h`. It is the integration boundary between the platform core, raw rc-core receive path, and hardware scancode receive path.

Risks and edge cases: bit masks and shifts directly encode hardware ABI. Parenthesization of register field macros matters when callers combine shifts and masks. All accessors assume `reg_base` is valid and mapped. Shared locking must cover multi-register updates in submodules to avoid inconsistent IRQ/filter/timing state.

Test signals: platform probe should report sensible core ID/revision, IRQ clear/enable should affect the expected sources, and both raw and hardware decoder builds should compile against the same private struct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/imon.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/imon.c

Purpose: USB driver for SoundGraph iMON multimedia IR/display devices. It supports rc-core scancode input for iMON and MCE/RC6 remotes, separate input devices for panel/knob/mouse/touchscreen functions, optional VFD/LCD display character devices, sysfs controls for display clock and 2.4 GHz RF association, two-interface devices, and USB suspend/resume.

Important APIs, types, and functions: `struct imon_context` is the device lifetime object, holding USB devices/endpoints/URBs, display state, RF state, rc-core device, input devices, key tracking, display/touch names, timers, device descriptor, refcount, disconnected flag, and RCU head. Descriptor tables (`imon_usb_dev_descr`) describe panel key maps and quirks such as packet delay and repeated-key suppression. File operations are `display_open()`, `display_close()`, `vfd_write()`, and `lcd_write()`. USB TX is centralized in `send_packet()` and `usb_tx_callback()`. Protocol/device controls include `send_associate_24g()`, `send_set_imon_clock()`, `associate_remote_*`, `imon_clock_*`, and `imon_ir_change_protocol()`. Input parsing functions include `stabilize()`, `imon_remote_key_lookup()`, `imon_mce_key_lookup()`, `imon_panel_key_lookup()`, `imon_mouse_event()`, `imon_touch_event()`, `imon_pad_to_keys()`, `imon_parse_press_type()`, and `imon_incoming_packet()`. USB lifecycle functions include RX callbacks for both interfaces, `imon_get_ffdc_type()`, `imon_set_display_type()`, `imon_init_rdev()`, `imon_init_idev()`, `imon_init_touch()`, `imon_find_endpoints()`, `imon_init_intf0()`, `imon_init_intf1()`, `imon_init_display()`, `imon_probe()`, `imon_disconnect()`, `imon_suspend()`, and `imon_resume()`.

Control flow: probe validates interface pairing, creates a new context for interface 0 or attaches interface 1 to the first context, locates endpoints, allocates and submits RX URBs, initializes input and rc-core devices, detects 0xffdc variants, optionally registers display sysfs and USB class devices, and stores interface data. RX callbacks process packets when the relevant interface is marked present, then resubmit URBs. `imon_incoming_packet()` distinguishes panel frames, iMON frames, MCE frames, touch frames, pad/mouse data, release frames, and RF association responses; it emits rc-core keydown/keyup or input events. Display writes take the context mutex, validate presence/open state, copy user data, format packets, and call `send_packet()`, which submits interrupt or control URBs and waits for completion. Disconnect marks the context disconnected, removes sysfs groups, aborts TX and RX URBs, unregisters devices by interface, deregisters display minors, and frees the context only after refcounted display file users have gone away.

State and persistence behavior: all state is volatile kernel memory. Device presence is split between `dev_present_intf0` and `dev_present_intf1`; display open state is `display_isopen`; protocol state is `rc_proto`; mouse/keyboard pad mode is `pad_mouse`; RF association state is `rf_isassociating`; key repeat/release state lives in `kc`, `last_keycode`, `rc_scancode`, `rc_toggle`, and `release_code`. The display character device lifetime is protected with `users`, `disconnected`, RCU in `display_open()`, and mutex locking around mutation. The touchscreen timer reports a release after `TOUCH_TIMEOUT`.

Dependencies and integration points: depends on USB core, input subsystem, rc-core, sysfs, timers, completions, mutex/spinlock/refcount/RCU primitives, and user-copy helpers. It exposes `/dev/lcdN` or VFD-style minors through USB class drivers, rc-core devices using `RC_MAP_IMON_PAD` or `RC_MAP_IMON_MCE`, input devices for panel/mouse/touch, module parameters (`debug`, `display_type`, `pad_stabilize`, `nomouse`, `pad_thresh`), and USB ID tables covering many SoundGraph products.

Risks and edge cases: the context lifetime is complex because open display files can outlive USB disconnect. `send_packet()` requires `ictx->lock` and intentionally unlocks neither while waiting; callers must avoid calling it without the mutex. 0xffdc devices reuse product IDs and are identified from received configuration bytes, so early RX and detection ordering matter. Static variables in `stabilize()` and some timing paths are shared across devices, which can couple multiple devices. `imon_disconnect()` calls `rc_unregister_device()` and then `rc_free_device()`; rc-core ownership expectations must be preserved. Packet parsing contains many product-specific special cases for release codes, mouse buttons, and panel repeats.

Test signals: test USB probe/disconnect with display file open, interface 0 and interface 1 ordering, suspend/resume URB resubmission, VFD 32-byte writes, LCD 8-byte writes, display clock sysfs validation, 2.4 GHz association, iMON versus MCE protocol switching, pad stabilization and mouse-mode toggle, 0xffdc variant detection, touchscreen release timer, and repeated panel-key suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/imon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/imon_raw.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/imon_raw.c

Purpose: USB raw-IR driver for early SoundGraph iMON IR-only devices. It converts 8-byte interrupt packets into rc-core raw pulse/space events so generic software decoders can decode the remote protocols.

Important APIs, types, and functions: `struct imon` stores the device, interrupt URB, raw rc-core device, 64-bit receive buffer, and physical path. `imon_ir_data()` reads the big-endian packet, ignores `0xff` packet markers, treats the high 40 bits as 250 us bit samples where 1 means space and 0 means pulse, coalesces runs into `ir_raw_event` durations, and marks idle/handles events when packet number 10 arrives. `imon_ir_rx()` handles URB completion and resubmits. `imon_probe()` finds the interrupt IN endpoint, allocates URB/buffer and `RC_DRIVER_IR_RAW` device, sets `RC_MAP_IMON_RSC`, `rx_resolution = 250`, submits the URB, and stores interface data. `imon_disconnect()` kills/frees the URB and buffer.

Control flow: each interrupt packet triggers `imon_ir_rx()`, which calls `imon_ir_data()` on success and then resubmits the same URB. `imon_ir_data()` repeatedly finds the next transition boundary with `fls64()`, alternates pulse/space state, stores filtered raw events, and on the final packet pushes idle state and `ir_raw_event_handle()`.

State and persistence behavior: the only runtime state is the URB, receive buffer, rc-core raw device, and physical path. No key or protocol state is stored in this driver; generic rc-core raw decoders own protocol state.

Dependencies and integration points: depends on USB core, rc-core raw event APIs, and input ID helpers. It binds USB device `04e8:ff30` and exposes an rc-core raw receiver with all software IR decoders allowed.

Risks and edge cases: the packet format assumes ten packets per station transmission and only the first five bytes contain IR samples. Missing packet 10 can delay idle handling. The code allocates the buffer with plain `kmalloc()` and frees it on errors/disconnect; error paths must free both URB and buffer. `usb_unlink_urb()` inside completion for shutdown statuses is conservative but unusual.

Test signals: test with an early iMON Station, verify raw event durations are multiples of 250 us, confirm idle after packet 10, disconnect during active URB, and decode through generic protocols using `ir-keytable`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/imon_raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-hix5hd2.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-hix5hd2.c

Purpose: platform raw-IR receiver driver for Hisilicon hix5hd2/hi3796cv300 controllers. It configures SoC IR hardware in raw symbol mode, drains hardware symbol FIFOs on interrupts, converts symbol low/high widths into rc-core raw pulse/space events, and registers an `RC_DRIVER_IR_RAW` device.

Important APIs, types, and functions: register and bit macros cover enable/config/data/interrupt/start registers. `struct hix5hd2_soc_data` supplies SoC clock register and extra-enable flag. `struct hix5hd2_ir_priv` stores MMIO base, IRQ, rc device, optional syscon regmap, clock, rate, and SoC data. `hix5hd2_ir_clk_enable()` toggles clock through syscon or common clock API. `hix5hd2_ir_enable()` writes enable bits. `hix5hd2_ir_config()` waits for not busy, programs raw mode, interrupt threshold, frequency divisor, unmasks interrupts, and starts capture. `hix5hd2_ir_rx_interrupt()` handles overflow, receive, and timeout interrupts, drains symbols, stores pulse/space events, sets idle on long symbols, clears interrupt causes, and handles raw events. Probe registers rc-core and IRQ; PM hooks disable/re-enable clocks and restart hardware.

Control flow: probe maps resources, gets IRQ/clock, enables the clock to sample rate, allocates rc-core raw device, registers it, requests the IRQ, and stores private data. rc-core open enables the clock and configures hardware; close disables clock. Interrupts read `IR_INTS`, handle overflow by flushing FIFO and reporting overflow, then read `IR_DATAH` count and `IR_DATAL` symbols for receive/timeout, converting packed low/high counts to 10 us raw durations. Suspend disables clocks; resume enables clocks, clears interrupts, and restarts capture.

State and persistence behavior: state is per-platform-device kernel memory. The hardware remains configured only while the rc device is open or resumed. No scancode state is kept; rc-core raw decoders own protocol state.

Dependencies and integration points: depends on platform device resources, device tree match data, optional `hisilicon,power-syscon` regmap, common clock, IRQ APIs, and rc-core raw event APIs. Device tree can provide `linux,rc-map-name`; otherwise the driver uses `RC_MAP_EMPTY`.

Risks and edge cases: bitwise expression precedence in config register construction must be read carefully; fields rely on masks/shifts. `hix5hd2_ir_config()` busy-waits up to 10 ms. Overflow handling requires reading `IR_DATAL` before clearing overflow because hardware does not clear FIFO. Probe enables the clock before registration and open enables it again, so clock state assumptions should be validated. PM resume uses both hardware clock helper and `clk_prepare_enable()`.

Test signals: test device tree match for both compatibles, raw decoding through rc-core, overflow behavior under heavy IR input, open/close clock gating, suspend/resume, and `linux,rc-map-name` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-hix5hd2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-imon-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-imon-decoder.c

Purpose: generic rc-core raw decoder and encoder for the iMON IR protocol. It parses 30-bit iMON waveforms, supports the iMON pad's keyboard/mouse toggle behavior, reports mouse events for stick movement in mouse mode, and emits `RC_PROTO_IMON` key events.

Important APIs, types, and functions: timing constants define 416 us units, 30 data bits, and a check-bit mask. `enum imon_state` models inactive, check, data, finished, and error states. `ir_imon_decode_scancode()` postprocesses the decoded 30-bit value, toggles stick keyboard mode for the keyboard/mouse key, converts stick movement to arrow scancodes in keyboard mode or input relative/mouse-button events in mouse mode, and calls `rc_keydown()`. `ir_imon_decode()` is the raw state machine. `ir_imon_encode()` builds raw events from a scancode using iMON check-bit rules. `ir_imon_register()` initializes per-device stick mode. `imon_handler` registers protocol, decode/encode hooks, carrier, raw register hook, and min timeout.

Control flow: raw rc-core dispatch passes timing events to `ir_imon_decode()`. It consumes events in unit-sized chunks, alternates check and data fields, validates dynamic check bits, enters error state on invalid timing/checks, and requires a long space before leaving error. When finished, it decodes/report the scancode and returns inactive. Module init registers the raw handler.

State and persistence behavior: per-rc-device decoder state lives in `dev->raw->imon`: state, bit count, bits, last check value, and stick keyboard flag. Mouse events are reported directly through the rc device's input device; scancode events go through rc-core.

Dependencies and integration points: depends on `rc-core-priv.h`, raw event timing helpers, input reporting for relative/mouse events, `lirc`/rc-core scancode emission through `rc_keydown()`, and module registration.

Risks and edge cases: protocol ambiguity means an incomplete message can look like one with low bits set, so the error-state long-space rule is important. Stick movement handling mutates `imon->bits` to arrow-key scancodes in keyboard mode. Mouse mode reports input relative/button events in addition to rc-keydown, so consumers may observe mixed input types.

Test signals: decode known iMON scancodes, encode/decode round trips, invalid check-bit handling, long-space recovery after error, keyboard/mouse toggle, stick arrow conversion, and mouse relative/button reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-imon-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-jvc-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-jvc-decoder.c

Purpose: generic rc-core raw decoder and encoder for the JVC pulse-distance IR protocol, including repeat detection.

Important APIs, types, and functions: constants define 16 bits, 525 us units, header, bit, trailer, and repeat spacing. `enum jvc_state` covers header, bit pulse/space, trailer, and repeat-check states. `ir_jvc_decode()` parses raw events, reverses byte bits with `bitrev8()`, emits `RC_PROTO_JVC` keydown on the first full frame, and treats later matching headerless frames as repeats. `ir_jvc_encode()` uses `ir_raw_gen_pd()` with `ir_jvc_timings`. `jvc_handler` registers decode/encode hooks, 38 kHz carrier, and timeout.

Control flow: the decoder requires an initial header pulse/space to start. It shifts 16 bits MSB-first, checks trailer pulse/space, emits the first scancode, stores `old_bits`, then moves to `STATE_CHECK_REPEAT`. A later event either resets on a new header or continues into another bit pulse sequence for repeat validation.

State and persistence behavior: per-device state includes count, bits, old bits, first-frame flag, toggle, and state. No persistent storage. Toggle is flipped at each new header.

Dependencies and integration points: depends on `rc-core-priv.h`, raw pulse-distance generator helpers, bit reversal, and rc-core keydown/repeat APIs.

Risks and edge cases: repeat validation requires repeated bits matching `old_bits`; mismatches reset as invalid. The source contains a visibly odd indentation before an `else`, but behavior is the standard header/no-header repeat branch. Timeout values must be long enough for JVC trailer spacing.

Test signals: decode a first JVC frame, repeated held-key frames, invalid repeat data, encode known scancodes, and verify carrier/min-timeout with transmit-capable devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-jvc-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-mce_kbd-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-mce_kbd-decoder.c

Purpose: raw decoder/encoder for the MCIR-2 keyboard and mouse protocol used by Microsoft Remote Keyboard for Windows Media Center. It converts IR keyboard reports to Linux input key events, mouse reports to relative/button events, emits lirc scancode events, and supports raw transmission.

Important APIs, types, and functions: `kbd_keycodes[256]` maps HID-like usage bytes to Linux keycodes. `mce_kbd_rx_timeout()` releases all keys after inactivity. `mce_kbd_mode()` interprets header mode. `ir_mce_kbd_process_keyboard_data()` reports modifier and up to two key bytes. `ir_mce_kbd_process_mouse_data()` decodes signed 7-bit X/Y and buttons. `ir_mce_kbd_decode()` is the Manchester-like state machine for 5-bit header plus 29-bit mouse or 32-bit keyboard body. `ir_mce_kbd_register()` initializes timer/spinlock; `ir_mce_kbd_unregister()` deletes the timer. `ir_mce_kbd_encode()` builds raw events using `ir_raw_gen_manchester()`. `mce_kbd_handler` registers keyboard and mouse protocol bits.

Control flow: decoding starts on the prefix pulse, reads header bits, selects keyboard or mouse body length, reads body bits, and on a finishing space processes the report. Keyboard reports update key state under `keylock`, arm or delete a release timer, send lirc scancode events, emit `MSC_SCAN`, and sync input. Mouse reports emit relative movement and button state. Raw registration initializes per-device support structures.

State and persistence behavior: per-device state in `dev->raw->mce_kbd` includes decode state, header/body/count, wanted bits, timer, and keylock. Keyboard key state persists in the input subsystem until updated or cleared by timeout.

Dependencies and integration points: depends on rc-core raw handler infrastructure, input subsystem key/relative reporting, lirc scancode events, timers, and spinlocks. Media keys that look like stock MCE RC6 are intentionally left to the RC6 decoder.

Risks and edge cases: key release depends on timer behavior; missed empty keyboard reports can leave keys pressed until timeout. The keycode table contains many reserved slots, so unknown usages are ignored or report reserved. Mouse signed conversion must preserve 7-bit two's-complement values. Header mode rejection prevents unrelated RC6-like frames from being misreported.

Test signals: decode keyboard single key, modifier combinations, all-keys-release report, timeout release, mouse movement/buttons, lirc scancode emission for both protocols, encode keyboard and mouse scancodes, and unregister while timer is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-mce_kbd-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-nec-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-nec-decoder.c

Purpose: generic rc-core raw decoder and encoder for normal NEC, NECX, and NEC32 pulse-distance IR protocols, including standard and NECX repeat handling.

Important APIs, types, and functions: constants define NEC timing and bit count. `enum nec_state` models header, bit, and trailer states. `ir_nec_decode()` parses timing events, distinguishes NEC and NECX header pulses, recognizes repeat spaces, accumulates 32 bits, converts bytes through `ir_nec_bytes_to_scancode()`, and emits `rc_keydown()` or `rc_repeat()`. `ir_nec_scancode_to_raw()` converts rc-core scancodes back to raw 32-bit NEC data. `ir_nec_encode()` uses `ir_raw_gen_pd()`. `nec_handler` registers all NEC-family protocol bits, 38 kHz carrier, and timeout.

Control flow: a header pulse transitions to header space. A repeat-length space jumps to trailer-pulse handling without reading 32 bits. Full frames shift bits MSB-first as durations are classified as zero or one spaces. Trailer space finalizes either a full scancode or a repeat. For NECX, one-bit repeat detection is tracked by `necx_repeat`.

State and persistence behavior: per-device NEC decoder state stores state, bit count, bits, NECX flag, and NECX repeat flag. No persistent storage beyond raw decoder state.

Dependencies and integration points: depends on bit reversal, `rc-core-priv.h`, `ir_nec_bytes_to_scancode()` from rc-core private helpers, raw pulse-distance generation, and rc-core keydown/repeat.

Risks and edge cases: NECX repeat logic differs from normal repeat and uses `NECX_REPEAT_BITS`. Inverse-byte interpretation is delegated to rc-core helper. Timing margins are protocol-specific and can reject noisy receivers. Encoder must honor the protocol enum to avoid ambiguous scancode interpretation.

Test signals: decode/encode NEC, NECX, NEC32; repeat frames for normal NEC and NECX; invalid timings; overflow reset; and transmit carrier defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-nec-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-rc5-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-rc5-decoder.c

Purpose: generic raw decoder and encoder for RC5, RC5X-20, and RC5 StreamZap Manchester-coded protocols.

Important APIs, types, and functions: constants define bit counts, 889 us unit, RC5X gap, and trailer. `ir_rc5_decode()` implements a Manchester state machine with special RC5X gap detection after eight bits, decodes protocol variants based on bit count and gap, extracts toggle/system/command/xdata fields, and emits `rc_keydown()`. Timing descriptors `ir_rc5_timings`, `ir_rc5x_timings`, and `ir_rc5_sz_timings` feed `ir_raw_gen_manchester()`. `ir_rc5_encode()` handles each protocol variant and returns `-EINVAL` for unsupported protocol enums. `rc5_handler` registers all three protocol bits.

Control flow: decoding starts on a pulse, consumes bit start/end units, checks for a trailer space, and at `STATE_FINISHED` selects RC5, RC5X, or RC5_SZ based on `is_rc5x` and `count`. Disabled protocol bits cause silent reset without keydown. Encoding splits RC5X into pre-gap and post-gap Manchester segments.

State and persistence behavior: per-device state includes state, count, bits, and `is_rc5x`. Toggle is emitted from frame bits. No persistent storage.

Dependencies and integration points: depends on rc-core raw Manchester helpers, enabled protocol masks, and keydown APIs. It complements the ImgTec hardware RC5 descriptor, which only supports standard RC5.

Risks and edge cases: RC5X detection after exactly `CHECK_RC5X_NBITS` is timing-sensitive. RC5 command extension bit handling inverts command bit semantics. Disabled protocol masks intentionally drop otherwise valid frames. StreamZap scancode is treated as raw enough for encoding.

Test signals: decode and encode RC5, RC5X-20, and RC5_SZ; verify toggle handling; test disabled enabled-protocol masks; and inject RC5X gap timing variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-rc5-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-rc6-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-rc6-decoder.c

Purpose: generic raw decoder and encoder for RC6 mode 0 and RC6-6A variants, including MCE, Zotac, and Kathrein customer-code handling.

Important APIs, types, and functions: constants define RC6 units, header/body lengths, prefix, toggle, suffix, mode masks, and customer-code masks. `rc6_mode()` classifies header mode. `ir_rc6_decode()` parses prefix, header, double-width toggle, variable body, and suffix; it emits `RC_PROTO_RC6_0`, `RC_PROTO_RC6_6A_20`, `RC_PROTO_RC6_6A_24`, `RC_PROTO_RC6_6A_32`, or `RC_PROTO_RC6_MCE`. MCE-style 32-bit customer codes clear the body toggle bit from the scancode and emit it as toggle. `ir_rc6_encode()` generates Manchester segments for mode 0 or mode 6A variants. `rc6_handler` registers all supported protocol bits.

Control flow: after prefix pulse/space, the decoder reads four header bits, a double-width toggle bit, chooses wanted body length (`16` for mode 0 or up to 128 for 6A), reads body bits until fixed length or suffix space, then validates and emits according to mode and body bit count. Encoding writes header, trailer/toggle bit, and body through timing descriptor segments.

State and persistence behavior: per-device state stores decode state, header, body, count, wanted bits, and toggle. The 32-bit body is bounded by `sizeof data->body`; longer 6A captures are rejected.

Dependencies and integration points: depends on rc-core raw helpers, Manchester generator, enabled protocol handling by rc-core, and input event consumers for MCE remotes. It is the primary software path for RC6 variants beyond the ImgTec hardware's limited RC6-0 descriptor.

Risks and edge cases: variable-length 6A support stops on suffix space and rejects bodies too large for `u32`. Customer-code classification changes protocol and toggle semantics for certain 32-bit values. First-pulse margin is wider than later units to tolerate receiver settling. Encoder does not synthesize MCE body toggle logic beyond using the provided scancode.

Test signals: decode/encode RC6-0, 6A-20/24/32, MCE customer codes, toggle extraction, unknown mode rejection, long 6A body rejection, and suffix timing variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-rc6-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-rcmm-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-rcmm-decoder.c

Purpose: generic raw decoder and encoder for RC-MM 12-, 24-, and 32-bit pulse-distance-like two-bit-symbol protocols.

Important APIs, types, and functions: timing constants define prefix and four symbol spaces. `rcmm_mode()` determines toggle interpretation for 32-bit mode. `rcmm_miscmode()` emits 12- or 24-bit scancodes when a non-symbol duration terminates shorter frames. `ir_rcmm_decode()` parses prefix, low/bump/value sequence, stores two bits per symbol, emits `RC_PROTO_RCMM32` with optional toggle or delegates shorter frames. `ir_rcmm_rawencoder()` and `ir_rcmm_encode()` produce raw events for each bit length. `rcmm_handler` registers all RC-MM protocol bits.

Control flow: decoder starts on prefix pulse plus low space, then alternates one-unit bump pulses with one of four value spaces. Count increments by two until 32 bits, or an unrecognized value duration triggers short-frame handling for 12/24 bits. Final pulse after 32 bits emits if RCMM32 is enabled.

State and persistence behavior: per-device state stores state, count, and accumulated bits. No persistent storage.

Dependencies and integration points: depends on rc-core private raw helpers, enabled protocol masks, and rc-core keydown APIs. It complements the ImgTec header's unsupported two-bit pulse-position code type; the ImgTec hardware path marks that code type broken.

Risks and edge cases: short-frame detection is based on a value-space miss, so noisy timings can choose between invalid and RCMM12/24 emission. `rcmm_mode()` changes whether bit 15 is treated as toggle. The decoder returns no events if none of the RCMM protocol bits are enabled.

Test signals: decode/encode RCMM12, RCMM24, RCMM32; toggle interpretation for mode frames; disabled-protocol no-op behavior; and symbol timing margins for each two-bit value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-rcmm-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-sanyo-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-sanyo-decoder.c

Purpose: generic raw decoder and encoder for Sanyo/Aiwa/Chinon pulse-distance IR, a NEC-timed 42-bit protocol with address and command inverse fields.

Important APIs, types, and functions: constants define 42-bit length and NEC-like timings. `ir_sanyo_decode()` parses header, bits, repeat space, trailer, reverses address/command bits, validates command inverse, and emits `RC_PROTO_SANYO`. `ir_sanyo_encode()` constructs raw fields with bit-reversed address, inverse address, command, and inverse command, then calls `ir_raw_gen_pd()`. `sanyo_handler` registers decode/encode hooks, 38 kHz carrier, and timeout.

Control flow: after header pulse/space, each bit pulse and bit space shifts data. A long repeat space with zero data count causes `rc_repeat()`. A complete 42-bit frame goes through trailer validation and checksum before keydown.

State and persistence behavior: per-device state stores current state, count, and bits. Repeat is emitted without local previous-key storage because rc-core owns last key state.

Dependencies and integration points: depends on bit reversal, rc-core raw pulse-distance helpers, and keydown/repeat APIs. The protocol has a sibling ImgTec hardware descriptor with matching validation.

Risks and edge cases: the decoder validates only command inverse; address inverse extraction is commented out, so address inverse corruption may not be caught here. Repeat spacing is very long relative to bit spaces. Encoding uses `~scancode` masks and bit reversal; field-width mistakes would corrupt inverse fields.

Test signals: decode valid Sanyo frames, invalid command inverse, repeat frames, encode/decode round trip, and noisy long-space behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-sanyo-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-sharp-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-sharp-decoder.c

Purpose: generic raw decoder and encoder for Sharp IR, including paired first/echo frames and a Denon-compatible first-frame variant.

Important APIs, types, and functions: constants define 15-bit message length, 40 us base unit, 320 us pulses, 1/2 ms bit periods, 40 ms echo spacing, and trailer spacing. `ir_sharp_decode()` parses pulse/space periods, records pulse length for period classification, validates first-frame exp/chk bits, waits for echo space, parses second frame, validates command/ext/check inversion, reverses address/command bits, and emits `RC_PROTO_SHARP`. `ir_sharp_encode()` emits the first and second 15-bit frames through `ir_raw_gen_pd()`. `sharp_handler` registers decode/encode hooks and timeout.

Control flow: decoding begins directly on a bit pulse without a leader. After 15 bits and a trailer pulse, the decoder moves through `STATE_ECHO_SPACE` to parse the second 15-bit echo. Final trailer space validates the pair and emits a scancode. Encoder emits two generated pulse-distance sequences: original command with exp/check bits and inverted command echo.

State and persistence behavior: per-device state stores state, count, bits, and last pulse length. The paired message is held in `bits` until the second half arrives.

Dependencies and integration points: depends on bit reversal, rc-core raw pulse-distance helpers, and keydown APIs. It aligns with the ImgTec Sharp descriptor, though the hardware descriptor reports only the first half.

Risks and edge cases: Sharp has no leader, increasing false-start risk. The first-frame check accepts both standard `(exp,chk) == 1,0` and Denon-style both zero. Pair validation masks only the command/ext/check region with `0x3ff`. Echo space is long and timeout-sensitive.

Test signals: decode standard Sharp, Denon-style first frames, invalid echo checksum, encode/decode round trip, and timeout around 40 ms echo gap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-sharp-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-sony-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-sony-decoder.c

Purpose: generic raw decoder and encoder for Sony SIRC 12-, 15-, and 20-bit pulse-length protocols.

Important APIs, types, and functions: constants define 600 us unit, 2.4 ms header pulse, pulse lengths for zero/one, and trailer space. `ir_sony_decode()` parses header, pulse-length bits, infers completion from remaining space, validates enabled protocol bits based on count, extracts device/subdevice/function with `bitrev8()`, and emits the correct Sony protocol. `ir_sony_encode()` converts rc-core scancodes back to raw bit layouts for each Sony variant and calls `ir_raw_gen_pl()`. `sony_handler` registers all Sony protocol bits, 40 kHz carrier, and timeout.

Control flow: after header pulse/space, bit pulses carry data value and bit spaces separate symbols. The decoder can enter finished state when the remaining space is longer than another bit. The final trailer chooses protocol by bit count and enabled-protocol mask.

State and persistence behavior: per-device state stores state, count, and bits. No persistent storage.

Dependencies and integration points: depends on bit reversal, rc-core raw pulse-length generator, enabled protocol masks, and keydown APIs. It shares scancode layout expectations with the ImgTec Sony descriptor.

Risks and edge cases: Sony variants are length-disambiguated, so enabled protocol masks can cause otherwise valid frames to be silently dropped. Completion detection relies on trailer space duration after subtracting bit spaces. Encoding assumes any non-12/non-15 protocol passed is Sony20.

Test signals: decode and encode Sony12/15/20, disabled protocol masks, noisy trailer spaces, scancode field extraction, and 40 kHz transmit carrier behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-sony-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-spi.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-spi.c

Purpose: SPI-backed IR LED transmitter driver. It registers a raw transmit-only rc-core device and converts pulse/space duration arrays into a binary SPI waveform that drives an IR LED through a regulator.

Important APIs, types, and functions: `struct ir_spi_data` stores carrier frequency, active-low flag, pulse/space 16-bit patterns, rc device, SPI device, and regulator. `ir_spi_tx()` converts microsecond durations to carrier cycles, allocates a `u16` transmit buffer, fills it with pulse or space words, enables the regulator, sends one SPI transfer at `freq * 16`, disables the regulator, and returns count or error. `ir_spi_set_tx_carrier()` validates carrier against SPI maximum speed. `ir_spi_set_duty_cycle()` computes pulse bitmask and handles active-low LED wiring. `ir_spi_probe()` reads regulator and device properties, allocates `RC_DRIVER_IR_RAW_TX`, wires callbacks, sets default carrier and duty cycle, and registers rc-core.

Control flow: userspace transmit through rc-core calls `tx_ir`, optionally after setting carrier or duty cycle. The SPI signal consists of `IR_SPI_BITS_PER_PULSE` bits per carrier period; duty cycle controls how many bits are high/low in the pulse word. The regulator is powered only around the SPI transfer.

State and persistence behavior: device state persists in devm-managed `ir_spi_data` for the SPI device lifetime. Carrier, duty cycle words, and active-low configuration remain until changed or device removal.

Dependencies and integration points: depends on SPI core, regulator framework, firmware properties (`led-active-low`, `duty-cycle`), rc-core raw TX API, and OF/SPI device IDs for `ir-spi-led`.

Risks and edge cases: `ir_spi_tx()` mutates the supplied duration buffer from microseconds to cycles, which is acceptable only if rc-core treats it as temporary. Large durations can allocate large buffers. Duty cycle calculation uses `GENMASK(bits, 0)` and `bits = duty_cycle * 15 / 100`; extreme duty-cycle values should be validated by callers or tested. Carrier must fit under `spi->max_speed_hz / 16`.

Test signals: transmit NEC/RC5 raw buffers, verify carrier frequency on a logic analyzer, test active-low and normal LED wiring, regulator enable/disable failure paths, large transmit buffers, invalid carrier zero/too-high, and property-provided duty cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-xmp-decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir-xmp-decoder.c

Purpose: raw decoder for the XMP IR protocol. It decodes two half-frames of variable nibble-duration data into a 32-bit scancode and treats nonzero toggle frames as repeats.

Important APIs, types, and functions: constants define 136 us unit, leader pulse, nibble prefix, half-frame space, and trailer space. `enum xmp_state` tracks inactive, leader pulse, and nibble-space states. `ir_xmp_decode()` stores 16 nibble durations, derives a divider from nibble 3, converts durations to nibble values, validates two checksum sums, verifies repeated subaddress, warns on unexpected OEM, constructs `addr << 24 | subaddr << 16 | obc1 << 8 | obc2`, and emits `rc_keydown()` for toggle 0 or `rc_repeat()` otherwise. `xmp_handler` registers a decode-only raw handler.

Control flow: a leader pulse starts collection. Each nibble is represented by a space duration after a leader. A half-frame space moves back to leader-pulse state and expects the second half. A trailer space finalizes exactly 16 collected nibbles. A 16-count half-frame is treated as a likely final key-up frame and rewinds to count 8 so the trailer can still be found.

State and persistence behavior: per-device state stores state, count, and duration/nibble array in `dev->raw->xmp`. No persistent storage and no encoder.

Dependencies and integration points: depends on rc-core private raw helpers and keydown/repeat APIs. It registers only `RC_PROTO_BIT_XMP`.

Risks and edge cases: divider derivation subtracts a fixed compensation and rejects values below 50, so receiver timing variation can affect decode. Toggle 9 frames are intentionally not distinguished in this implementation despite protocol comments. There is no encode path. OEM mismatch only logs a warning, not a rejection.

Test signals: decode known XMP full frames, repeat/toggle frames, checksum failures, subaddress mismatches, final half-frame behavior, and noisy divider values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir-xmp-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir_toy.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ir_toy.c

Purpose: USB rc-core driver for Dangerous Prototypes USB IR Toy and IR Droid devices. It handles sampling-mode receive, raw transmit, carrier setting, firmware/protocol setup, and rc-core raw receiver registration.

Important APIs, types, and functions: `struct irtoy` stores USB device, rc device, bulk URBs, input/output buffers, command completion, state machine, pulse polarity, TX buffer/progress, version fields, and physical path. `irtoy_response()` dispatches incoming bulk data by state: command replies, raw sample data, or TX flow-control/result messages. `irtoy_out_callback()` completes no-response commands. `irtoy_in_callback()` handles input URB completion and resubmission. `irtoy_command()` sends a command and waits up to 500 ms. `irtoy_setup()` resets the device, reads version, and enters sample mode. `irtoy_tx()` converts microsecond durations to 21 us units, re-enters sample mode to avoid a known hang, starts TX, streams chunks as requested by the device, validates emitted byte count, and resets on errors. `irtoy_tx_carrier()` programs carrier. Probe locates 64-byte bulk endpoints, allocates objects, submits input URB, sets up hardware, validates firmware >= v20, registers rc-core, and stores interface data. Disconnect unregisters rc-core, kills/frees URBs, and frees buffers.

Control flow: after probe, the input URB is always live. In receive state, incoming 16-bit big-endian durations are alternated as pulse/space; `0xffff` marks timeout/space reset; events are stored with timeout handling and dispatched. Commands temporarily change `state` and complete via incoming replies or output callback. Transmit switches out and back into sample mode, sends `COMMAND_TXSTART`, then `irtoy_response()` feeds output chunks whenever the device reports available packet space until an emitted count and success reply arrive.

State and persistence behavior: `state`, `pulse`, `tx_buf`, `tx_len`, `emitted`, and version fields persist in `struct irtoy` during device lifetime. `tx_buf` points into a temporary buffer during synchronous transmit; the command completion ensures the buffer is not freed until TX finishes or fails. No persistent userspace storage.

Dependencies and integration points: depends on USB bulk APIs, completions, unaligned big-endian helpers, rc-core raw RX/TX APIs, and USB IDs for IR Toy/IR Droid CDC data interfaces. rc-core exposes all software decoders, default `RC_MAP_RC6_MCE`, TX carrier callback, and RX timeout bounds.

Risks and edge cases: state machine correctness is critical because command replies, raw samples, and TX flow control share the same input endpoint. The TX buffer pointer is advanced as a `void *`, relying on compiler support common in the kernel. If emitted byte count differs from expected, the driver resets the device. Firmware below v20 is rejected. Input URB is submitted before setup, so setup responses and raw data share callbacks immediately.

Test signals: probe firmware v20+ and too-old firmware, receive raw samples, transmit long buffers requiring multiple chunks, carrier setting below minimum and normal values, command timeout, disconnect during TX, and recovery after emitted-count mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ir_toy.c -->
