# Research: subset-b-004799

Grouped research report for subset B work item `subset-b-004799`. Each section is source-tree aligned and wrapped for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/dma.c

## Purpose
`dma.c` implements the software side of the Broadcom `brcmsmac` DMA engine. It allocates and initializes DMA descriptor rings, programs D11/BCMA DMA64 registers, maps and unmaps SKB payload buffers, tracks ring indices, posts receive buffers, drains completed receive frames, queues transmit frames, batches AMPDU transmit frames, reclaims completed descriptors, and exposes lightweight counters through `struct dma_pub`.

Although the file retains comments about 32-bit and 64-bit addressing, the executable implementation is for DMA64 descriptor rings. The code is performance- and correctness-critical because it is the handoff point between mac80211/common-driver packet state and hardware-owned DMA descriptors.

## Important APIs, Types, and Functions
- Register and descriptor constants define DMA64 control/status bits, descriptor flags, address-extension fields, receive frame status masks, and the 8 KiB ring alignment requirement.
- `struct dma64desc` is the hardware-read descriptor format: `ctrl1`, `ctrl2`, `addrlow`, and `addrhigh`, all little-endian.
- `struct dma_info` is the private runtime object behind `struct dma_pub`. It stores the BCMA core, DMA device, AMPDU session, TX/RX register offsets, coherent descriptor rings, software SKB pointer arrays, ring indices, address offsets, alignment state, RX sizing, and exported counters.
- Ring helpers `txd()`, `rxd()`, `nexttxd()`, `prevtxd()`, `nextrxd()`, `ntxdactive()`, and `nrxdactive()` implement power-of-two ring wrap arithmetic.
- Descriptor setup helpers:
  - `parity32()` and `dma64_dd_parity()` compute optional descriptor parity.
  - `_dma_ctrlflags()` updates DMA control flags and probes parity support by writing the DMA control register.
  - `_dma_isaddrext()` and `_dma64_addrext()` detect address-extension support.
  - `_dma_descriptor_align()` probes whether descriptor base low bits are writable, selecting 16-byte, 4 KiB, or 8 KiB alignment behavior.
  - `dma_alloc_consistent()`, `dma_ringalloc()`, and `dma64_alloc()` allocate coherent descriptor rings with the hardware alignment and boundary constraints.
  - `dma64_dd_upd()` writes a descriptor for a mapped buffer and handles PCI address-extension bits.
  - `_dma_ddtable_init()` programs descriptor-ring base addresses into TX or RX DMA registers.
- Lifecycle APIs exported through `dma.h`:
  - `dma_attach()` allocates `dma_info`, packet pointer arrays, descriptor rings, address offsets, alignment properties, and the AMPDU session.
  - `dma_detach()` frees coherent rings, pointer arrays, and the private object.
  - `dma_txinit()`, `dma_rxinit()`, `dma_txreset()`, and `dma_rxreset()` initialize or quiesce the engines.
  - `dma_txsuspend()`, `dma_txresume()`, and `dma_txsuspended()` control the TX suspend bit.
- Receive path:
  - `_dma_rxenable()` builds the RX control word.
  - `dma_rxfill()` allocates SKBs, reserves extra headroom, maps them for `DMA_FROM_DEVICE`, writes RX descriptors, and advances the hardware RX pointer.
  - `_dma_getnextrxp()` and `dma64_getnextrxp()` retrieve completed RX SKBs, unmap their buffers, poison descriptor addresses, and advance `rxin`.
  - `dma_rx()` parses the DMA-provided frame length, trims SKBs, handles multi-descriptor receive frames when enabled, drops giant frames otherwise, and appends complete frames to the caller's SKB queue.
  - `dma_rxreclaim()` force-drains all posted RX buffers.
- Transmit path:
  - `dma_txenq()` maps an SKB for `DMA_TO_DEVICE`, writes a SOF/EOF/IOC descriptor, saves the SKB in the TX pointer array, and advances `txout`.
  - `dma_txfast()` is the main TX entry. It rejects empty packets, checks descriptor availability, queues normal packets directly, or queues AMPDU packets through `prep_ampdu_frame()`.
  - `ampdu_finalize()` lets the common AMPDU layer finalize headers, enqueues all queued AMPDU SKBs into DMA, writes the hardware TX pointer, and resets AMPDU session state.
  - `dma_kick_tx()` starts a pending AMPDU session if the DMA engine is idle.
  - `dma_getnexttxp()` reclaims descriptors based on all, transmitted, or transferred ranges, unmaps TX buffers, returns associated SKBs, and updates `txavail`.
  - `dma_txreclaim()` frees reclaimed SKBs unless unframed mode is active.
  - `dma_walk_packets()` visits in-flight TX packets and passes their `ieee80211_tx_info` control block to a caller callback.
- Counter and variable helpers:
  - `dma_counterreset()` clears exported RX/TX error counters.
  - `dma_getvar("&txavail")` returns the address of exported TX availability for external flow-control integration.

## Control Flow
Attach begins with `dma_attach()`. The caller provides register base offsets, ring sizes, RX buffer sizing, post count, and RX offset. `dma_attach()` allocates `dma_info`, copies the caller's name, selects DMA64 mode from the BCMA core, computes PCI descriptor/data address offsets, probes address-extension and descriptor-alignment behavior, allocates TX/RX SKB pointer vectors, allocates coherent descriptor rings, rejects unsupported high physical addresses when address extension is unavailable, and initializes the AMPDU session.

Initialization is split per direction. `dma_txinit()` resets TX indices and `txavail`, clears the TX descriptor ring, writes the descriptor table before or after enabling the engine depending on alignment behavior, and enables TX with parity disabled when `DMA_CTRL_PEN` is not active. `dma_rxinit()` resets RX indices, clears the RX ring, optionally writes the descriptor base before enabling, enables RX with overflow/parity controls, and writes the descriptor base after enabling when required by the hardware.

The RX steady-state path is `dma_rxfill()` followed by interrupt-driven calls into `dma_rx()`. `dma_rxfill()` calculates how many buffers are needed to reach `nrxpost`, allocates SKBs, reserves optional extra headroom for later bridging/TX header needs, clears the length field, DMA-maps the buffer, records the SKB in `rxp[rxout]`, writes the descriptor, advances the local `rxout`, commits `di->rxout`, and updates the hardware last descriptor pointer. `dma_rx()` pulls completed buffers until one full frame is assembled. If the length spans multiple buffers and `DMA_CTRL_RXMULTI` is disabled, it frees the gathered buffers, increments `rxgiants`, and continues with the next frame.

The TX steady-state path starts at `dma_txfast()`. For normal packets, `dma_txenq()` maps the packet, fills one descriptor, stores the SKB, advances `txout`, and `dma_txfast()` writes the hardware TX pointer. For AMPDU packets, `prep_ampdu_frame()` accumulates the SKB in the AMPDU session. The session is finalized and kicked when it reaches the maximum AMPDU frame count, descriptor availability reaches zero, or the hardware TX engine is idle. Reclaim flows through `dma_getnexttxp()`, which uses hardware current/active descriptor pointers unless the caller requests `DMA_RANGE_ALL`.

Reset and teardown paths quiesce hardware before software memory is released. `dma_txreset()` requests TX suspend, waits for disabled/idle/stopped state, disables the engine, waits for disabled state, and delays for the final transaction. `dma_rxreset()` disables RX and waits for disabled state. `dma_txreclaim()` and `dma_rxreclaim()` are expected to drain SKBs before or around detach. `dma_detach()` only frees descriptor rings and pointer arrays; it does not itself walk and free still-posted SKBs.

## State and Persistence
All state is runtime kernel state. There is no on-disk persistence. Durable-looking values such as DMA counters last only for the lifetime of the DMA object and can be reset with `dma_counterreset()`.

Important mutable state includes `txin`, `txout`, `rxin`, `rxout`, `txavail`, `txp[]`, `rxp[]`, coherent descriptor contents, descriptor physical addresses, DMA address offsets, control flags, RX buffer sizing/headroom, `nrxpost`, `rxoffset`, and the embedded `brcms_ampdu_session`. Hardware state is mirrored through DMA64 control, status, descriptor base, and pointer registers accessed via `bcma_read32()` and `bcma_write32()`.

## Dependencies and Integration Points
- Depends on Linux DMA APIs: `dma_alloc_coherent()`, `dma_free_coherent()`, `dma_map_single()`, `dma_unmap_single()`, and `dma_mapping_error()`.
- Depends on BCMA register access and device metadata through `struct bcma_device`, `core->dma_dev`, `BCMA_IOST`, `SISF_DMA64`, and PCI host type information.
- Uses SKB allocation/free helpers from `brcmu_utils`: `brcmu_pkt_buf_get_skb()` and `brcmu_pkt_buf_free_skb()`.
- Integrates with mac80211 through `IEEE80211_SKB_CB()` and `IEEE80211_TX_CTL_AMPDU`.
- Integrates with the common brcmsmac layer through `struct brcms_c_info`, `wlc->hw`, `brcms_c_ampdu_reset_session()`, `brcms_c_ampdu_add_frame()`, `brcms_c_ampdu_finalize()`, and tracepoint `trace_brcms_ampdu_session()`.
- Includes `debug.h` and emits DMA debug messages through `brcms_dbg_dma()`.
- Public callers use the interface declared in `dma.h`; descriptor internals remain private to this file.

## Risks and Edge Cases
- Ring arithmetic assumes ring sizes are powers of two. Non-power-of-two `ntxd` or `nrxd` values would break `xxd()` wrapping.
- Descriptor alignment and pointer-base handling are hardware-specific. Incorrect `aligndesc_4k`, `xmtptrbase`, or `rcvptrbase` behavior can make hardware consume or report the wrong descriptor.
- Address-extension handling is subtle. PCI physical addresses above the low DMA window require correct high-bit folding into descriptor or control AE fields; unsupported high addresses cause attach failure.
- `dma_rxfill()` may return early on DMA mapping failure after preparing earlier descriptors in local variables but before committing `di->rxout` and the hardware pointer. That path deserves fault-injection coverage.
- `dma_txenq()` frees an SKB on DMA mapping failure but has a `void` return type, so `dma_txfast()` cannot report that specific failure to its caller.
- `dma_detach()` assumes packet buffers have already been reclaimed or are otherwise not live; direct detach with populated `txp[]` or `rxp[]` would leak SKBs.
- RX length is read from device-written packet data. The BCM47XX workaround `dma_spin_for_len()` can busy-wait until hardware writes the length.
- Multi-buffer RX is disabled unless `DMA_CTRL_RXMULTI` is set. Oversized frames become drops and increment `rxgiants`.
- `dma_walk_packets()` walks only descriptor-ring SKBs and does not include SKBs queued in the AMPDU session list.
- Suspend/reset waits use fixed spin limits. Hardware stalls or missed state transitions surface as failed reset rather than recovery inside this file.

## Test Signals
- Build coverage with `CONFIG_BRCMSMAC`, `CONFIG_BRCMDBG`, and `CONFIG_BCM47XX` where possible.
- Attach/init tests should validate ring allocation alignment, descriptor base programming, PCI address-offset behavior, address-extension probing, and cleanup on every allocation failure point.
- RX tests should cover normal single-buffer frames, multi-buffer frames with and without `DMA_CTRL_RXMULTI`, giant-frame drops, ring wrap, empty ring refill failure, DMA mapping failure, and `dma_rxreclaim()`.
- TX tests should cover descriptor exhaustion, ring wrap, DMA mapping failure, normal packet enqueue/reclaim, `DMA_RANGE_TRANSMITTED`, `DMA_RANGE_TRANSFERED`, `DMA_RANGE_ALL`, and unframed reclaim mode.
- AMPDU tests should exercise aggregation by frame count, descriptor pressure, idle-engine kick, `dma_kick_tx()`, and AMPDU flush/reclaim interaction.
- Hardware tests should observe DMA64 status/control register transitions during `dma_txreset()`, `dma_rxreset()`, `dma_txsuspend()`, and `dma_txresume()`.
- Useful observability includes `brcms_dbg_dma()` messages, exported `txavail`, `rxnobuf`, `rxgiants`, `txnobuf`, and the AMPDU tracepoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/dma.h

## Purpose
`dma.h` is the public DMA interface for the `brcmsmac` common driver. It declares the register layout needed by the implementation, the exported DMA status/counter structure, TX reclaim range semantics, direction constants, and all packet lifecycle entry points used by the rest of the driver.

The header hides `struct dma_info` and exposes only `struct dma_pub *`, keeping descriptor-ring implementation details private to `dma.c`.

## Important APIs, Types, and Functions
- `DMA_TX` and `DMA_RX` identify map/unmap or allocation direction.
- `struct dma32diag` describes diagnostic FIFO access registers for 32-bit-era hardware documentation, although this subset's implementation code uses DMA64.
- `struct dma64regs` defines the per-channel DMA64 register layout: `control`, `ptr`, `addrlow`, `addrhigh`, `status0`, and `status1`.
- `enum txd_range` tells `dma_getnexttxp()` and `dma_txreclaim()` how far to reclaim:
  - `DMA_RANGE_ALL` reclaims all posted descriptors.
  - `DMA_RANGE_TRANSMITTED` uses the hardware current descriptor pointer.
  - `DMA_RANGE_TRANSFERED` uses the active descriptor pointer to avoid reclaiming a descriptor still transferring.
- `struct dma_pub` is the read-mostly public state: `txavail`, `dmactrlflags`, RX counters `rxgiants`/`rxnobuf`, and TX counter `txnobuf`.
- Lifecycle declarations:
  - `dma_attach()` and `dma_detach()`.
  - `dma_txinit()`, `dma_rxinit()`, `dma_txreset()`, `dma_rxreset()`.
  - `dma_txsuspend()`, `dma_txresume()`, and `dma_txsuspended()`.
- Packet operations:
  - `dma_rxfill()`, `dma_rx()`, `dma_rxreclaim()`.
  - `dma_txfast()`, `dma_kick_tx()`, `dma_txpending()`, `dma_getnexttxp()`, and `dma_txreclaim()`.
  - `dma_walk_packets()` for caller-supplied mutation/inspection of in-flight TX packet metadata.
- Counter and variable helpers:
  - `dma_counterreset()`.
  - `dma_getvar()`, currently used for address-of access to `txavail`.
- `dma_spin_for_len()` is an inline BCM47XX workaround that waits for DMA to write a packet length into the RX buffer and converts it to little endian.

## Control Flow
This header has no standalone control flow. Its declarations define the expected ordering for DMA users:

1. Create a DMA object with `dma_attach()`.
2. Initialize TX and/or RX channels with `dma_txinit()` and `dma_rxinit()`.
3. Keep RX populated with `dma_rxfill()` and drain completed frames with `dma_rx()`.
4. Queue transmit packets with `dma_txfast()`, optionally force an outstanding AMPDU batch with `dma_kick_tx()`, and reclaim completed packets with `dma_txreclaim()` or `dma_getnexttxp()`.
5. During reset, suspend, or teardown, stop engines with `dma_txreset()`/`dma_rxreset()`, reclaim packet buffers, and finally call `dma_detach()`.

The inline BCM47XX helper is invoked from the RX path after reading the initial packet length. On affected systems it can spin until hardware updates the length field.

## State and Persistence
The header defines the public DMA state shape but owns no state itself. `struct dma_pub` fields are embedded in the private object allocated by `dma.c`. They persist only while the DMA handle exists and are resettable runtime counters or live flow-control values.

## Dependencies and Integration Points
- Includes Linux `delay.h` and `skbuff.h` for `udelay()` and `struct sk_buff`.
- Includes local `types.h` for forward declarations such as `struct brcms_c_info`.
- Used by common brcmsmac code that attaches DMA rings, sends packets, refills RX, handles interrupts, and performs reset/teardown.
- The `dma_spin_for_len()` workaround uses `KSEG1ADDR()` and is compiled only for `CONFIG_BCM47XX`, tying the interface to MIPS-style uncached access on that platform.

## Risks and Edge Cases
- `struct dma_pub` is described as read-only to consumers, but it is not enforced by the type system; callers can mutate counters or control flags if they keep a non-const pointer.
- Correct reclaim behavior depends on choosing the right `enum txd_range`. Reclaiming `DMA_RANGE_ALL` while hardware still owns descriptors can corrupt TX completion ownership.
- `dma_getvar()` exposes an address inside the private object by name string. That is flexible but bypasses normal type safety.
- The RX length spin workaround can busy-wait indefinitely if an affected system reports a ready packet whose length never appears.
- The header does not encode locking rules. Callers must follow the surrounding driver's perimeter lock and interrupt synchronization conventions.

## Test Signals
- Compile tests should ensure all users include this header rather than relying on private `dma.c` definitions.
- API-order tests should cover attach/init/fill/send/reclaim/reset/detach sequencing.
- Platform tests should include BCM47XX behavior when possible to exercise `dma_spin_for_len()`.
- Static analysis should flag writes to `struct dma_pub` outside `dma.c` unless they are deliberate control-flag setup.
- Reclaim tests should verify all three `enum txd_range` values against hardware pointer progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/led.c

## Purpose
`led.c` connects `brcmsmac` radio-state LED support to the Linux LED and GPIO subsystems. It discovers the board-defined radio LED GPIO from SPROM GPIO behavior fields, requests that line from the BCMA chipcommon GPIO controller, registers an LED class device, and lets the mac80211 radio LED trigger control the GPIO.

## Important APIs, Types, and Functions
- Constants:
  - `BRCMS_LED_NO` limits SPROM scanning to GPIO0 through GPIO3.
  - `BRCMS_LED_BEH_MASK` extracts the LED behavior code.
  - `BRCMS_LED_AL_MASK` extracts the active-low polarity bit.
  - `BRCMS_LED_RADIO` identifies the "radio enabled" LED behavior.
- `brcms_radio_led_ctrl(struct brcms_info *wl, bool state)` sets the stored GPIO descriptor high or low and returns silently when no descriptor is present.
- `brcms_led_brightness_set()` is the LED subsystem callback. It converts a `struct led_classdev *` back to `struct brcms_info` with `container_of()` and calls `brcms_radio_led_ctrl()`.
- `brcms_led_register(struct brcms_info *wl)`:
  - Reads SPROM GPIO behavior values from `wl->wlc->hw->d11core->bus->sprom`.
  - Finds the first GPIO configured as a radio LED.
  - Converts active-low SPROM polarity into `GPIO_ACTIVE_LOW`.
  - Requests the GPIO with `gpiochip_request_own_desc()`.
  - Builds a stable LED name `brcmsmac-%s:radio`.
  - Uses `ieee80211_get_radio_led_name()` as the default trigger.
  - Registers `wl->led_dev` with `led_classdev_register()`.
- `brcms_led_unregister(struct brcms_info *wl)` unregisters the LED class device if registered and frees the owned GPIO descriptor if present.

## Control Flow
Probe-time code in `mac80211_if.c` calls `brcms_led_register()` after `brcms_attach()` succeeds. Registration walks SPROM GPIO0-3 values and exits with `-ENODEV` if no radio LED behavior is configured. When a candidate exists, the function requests the line from the BCMA GPIO chip as an output initially low, populates the LED class device, and registers it against the wiphy device.

Runtime LED changes enter through `brcms_led_brightness_set()`, not through driver-specific control paths. The callback treats any nonzero brightness as true and sets the radio GPIO to logical 1; GPIO descriptor polarity handles active-low conversion because the descriptor was requested with the matching lookup flag.

Remove-time code calls `brcms_led_unregister()` before unregistering the mac80211 hardware. The unregister path tears down the LED class device first, then releases the GPIO descriptor.

## State and Persistence
LED state is runtime-only. `wl->radio_led.name` stores the generated LED name, `wl->radio_led.gpiod` stores the owned GPIO descriptor, and `wl->led_dev` stores LED subsystem registration state. The board's SPROM GPIO behavior is treated as persistent hardware configuration but this file only reads it.

## Dependencies and Integration Points
- Depends on mac80211 for the radio LED trigger name through `ieee80211_get_radio_led_name()`.
- Depends on the Linux LED class through `struct led_classdev`, `led_classdev_register()`, and `led_classdev_unregister()`.
- Depends on GPIO descriptor and GPIO chip APIs: `gpiochip_request_own_desc()`, `gpiochip_free_own_desc()`, and `gpiod_set_value()`.
- Depends on BCMA chipcommon and SPROM fields through `struct bcma_drv_cc`, `struct gpio_chip`, and `struct ssb_sprom`.
- Uses wiphy logging and device lookup through `wl->wiphy`, `wiphy_name()`, `wiphy_dev()`, `wiphy_err()`, and `wiphy_info()`.
- Public declarations and build-time stubs live in `led.h`; `mac80211_if.c` invokes registration and unregister.

## Risks and Edge Cases
- `brcms_bcma_probe()` ignores the return value from `brcms_led_register()`, so LED failure does not fail device probe. That is appropriate for optional LEDs but can hide GPIO/LED registration problems unless logs are checked.
- If `led_classdev_register()` fails after the GPIO descriptor is acquired, the function returns an error while leaving `wl->radio_led.gpiod` populated. Later `brcms_led_unregister()` can release it, but the immediate error path does not free it locally.
- The code chooses the first GPIO0-3 SPROM entry with radio behavior. Boards with multiple matching entries cannot select later ones.
- The name buffer is 32 bytes. `snprintf()` prevents overflow, but very long wiphy names may be truncated.
- The brightness callback assumes `struct led_classdev` is embedded in `struct brcms_info` as `led_dev`, which is true for this driver.
- `gpiod_set_value()` may sleep depending on GPIO provider semantics; chipcommon GPIOs are expected to be safe for this LED callback usage.

## Test Signals
- Build with and without `CONFIG_BRCMSMAC_LEDS` to validate both implementation and inline stubs.
- Probe tests with SPROM GPIO entries for no LED, active-high radio LED, and active-low radio LED.
- Runtime tests should verify `/sys/class/leds/brcmsmac-*:radio` appears when SPROM config exists, uses the mac80211 radio trigger by default, and toggles the correct GPIO.
- Error injection should cover GPIO request failure and LED class registration failure.
- Remove/unload tests should verify the LED class device disappears and the GPIO descriptor is released without use-after-free callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/led.h

## Purpose
`led.h` declares the small LED support interface for `brcmsmac`. It provides the per-device radio LED descriptor state and hides LED support behind `CONFIG_BRCMSMAC_LEDS` so the rest of the driver can call registration and unregister functions unconditionally.

## Important APIs, Types, and Functions
- Forward declaration `struct gpio_desc` avoids requiring all users of the header to include GPIO descriptor headers.
- `struct brcms_led` stores:
  - `name[32]`, the generated LED class device name.
  - `gpiod`, the GPIO descriptor owned by the radio LED.
- When `CONFIG_BRCMSMAC_LEDS` is enabled:
  - `brcms_led_register(struct brcms_info *wl)` is implemented in `led.c`.
  - `brcms_led_unregister(struct brcms_info *wl)` is implemented in `led.c`.
- When LED support is disabled:
  - `brcms_led_unregister()` compiles to a no-op.
  - `brcms_led_register()` returns `-ENOTSUPP`.

## Control Flow
The header itself has no control flow beyond compile-time selection. It lets `mac80211_if.c` call LED registration during probe and unregister during remove regardless of kernel configuration. With LED support disabled, those calls become harmless stubs.

## State and Persistence
The header defines `struct brcms_led`, which is embedded in `struct brcms_info` in `mac80211_if.h`. The state is runtime-only and persists only while the wireless device object exists.

## Dependencies and Integration Points
- Included by `mac80211_if.h` so `struct brcms_info` can embed `struct brcms_led`.
- Included by `led.c` for the implementation.
- Depends on `struct brcms_info` being declared before prototype use in translation units that include the header. The header does not provide a forward declaration for it.
- Integrates with Kconfig symbol `CONFIG_BRCMSMAC_LEDS`.

## Risks and Edge Cases
- The disabled stub returns `-ENOTSUPP`, but the probe path ignores the return value. Callers that begin treating LED registration as mandatory must account for this build-time behavior.
- The no-op unregister stub uses an empty inline body, so callers cannot tell whether LED support was compiled in.
- `name[32]` is fixed by the ABI of this internal struct; implementation code must continue to use bounded string operations.

## Test Signals
- Compile tests with `CONFIG_BRCMSMAC_LEDS=y` and disabled.
- Static checks should confirm all callers tolerate `brcms_led_register()` returning optional-feature errors.
- Runtime LED tests belong to `led.c`; this header's main signal is that probe/remove builds cleanly in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/mac80211_if.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/mac80211_if.c

## Purpose
`mac80211_if.c` is the Linux-facing glue for the Broadcom `brcmsmac` soft-MAC driver. It registers the BCMA driver, allocates and registers `ieee80211_hw`, exposes `ieee80211_ops`, loads firmware, initializes supported bands/rates/capabilities, bridges mac80211 callbacks into the common `brcms_c_*` core, manages interrupts and tasklet bottom halves, provides timer wrappers for common code, handles rfkill, and performs module/probe/remove lifecycle work.

## Important APIs, Types, and Functions
- Module and device registration:
  - `brcms_coreid_table` matches Broadcom BCMA 802.11 cores with revisions 17, 23, and 24.
  - `brcms_bcma_driver` supplies `.probe`, `.remove`, `.suspend`, and `.resume`.
  - `brcms_module_init()` initializes debugfs and schedules asynchronous driver registration through `brcms_driver_work`.
  - `brcms_module_exit()` cancels registration work, unregisters the BCMA driver, and exits debugfs.
- Channel/rate capability tables:
  - `brcms_2ghz_chantable`, `brcms_5ghz_nphy_chantable`, and `legacy_ratetable` describe cfg80211-visible channels and rates.
  - `brcms_band_2GHz_nphy_template` and `brcms_band_5GHz_nphy_template` provide HT capabilities and MCS defaults.
  - `ieee_hw_rate_init()` copies band templates into `wlc->bandstate[]` and adjusts LCN single-stream capabilities.
  - `ieee_hw_init()` sets mac80211 hardware flags, queues, headroom, interface modes, CQM RSSI list support, and minstrel_ht rate control.
- Attach/remove and resource cleanup:
  - `brcms_bcma_probe()` validates the BCMA core, allocates `ieee80211_hw`, stores drvdata, calls `brcms_attach()`, and starts optional LED registration.
  - `brcms_attach()` initializes locks/tasklet/waitqueue, attaches common driver state with `brcms_c_attach()`, requests IRQ, registers the common module, initializes mac80211 hardware, sets regulatory data and permanent address, registers the hardware, and creates debugfs files.
  - `brcms_remove()` unregisters LED/rfkill/mac80211 state, frees driver resources, clears drvdata, and frees `ieee80211_hw`.
  - `brcms_free()` releases ucode data, IRQ, tasklet, debugfs/common modules, common resources, pending callbacks, and timer allocations.
- Firmware helpers:
  - `brcms_request_fw()` requests `brcm/bcm43xx-0.fw` and `brcm/bcm43xx_hdr-0.fw`, records header entry counts, initializes ucode data, and releases firmware blobs.
  - `brcms_release_fw()` releases all firmware references.
  - `brcms_ucode_init_buf()` copies a firmware section by tag into driver-owned memory.
  - `brcms_ucode_init_uint()` reads a 32-bit firmware section value by tag.
  - `brcms_check_firmwares()` validates firmware/header pairing, header alignment, file size bounds, section bounds, and `fw_cnt`.
  - `brcms_ucode_free_buf()` frees copied ucode buffers.
- mac80211 operations in `brcms_ops`:
  - TX/start/stop: `brcms_ops_tx()`, `brcms_ops_start()`, `brcms_ops_stop()`.
  - Interface: `brcms_ops_add_interface()` and `brcms_ops_remove_interface()`.
  - Configuration: `brcms_ops_config()`, `brcms_ops_bss_info_changed()`, `brcms_ops_configure_filter()`, `brcms_ops_conf_tx()`.
  - Scan: `brcms_ops_sw_scan_start()` and `brcms_ops_sw_scan_complete()`.
  - STA/AMPDU: `brcms_ops_sta_add()` and `brcms_ops_ampdu_action()`.
  - rfkill/flush/TSF/TIM: `brcms_ops_rfkill_poll()`, `brcms_ops_flush()`, `brcms_ops_get_tsf()`, `brcms_ops_set_tsf()`, and `brcms_ops_beacon_set_tim()`.
  - Channel context hooks are mac80211 emulation helpers and `.wake_tx_queue` uses `ieee80211_handle_wake_tx_queue`.
- Interrupt and bottom-half handling:
  - `brcms_isr()` calls `brcms_c_isr()` under `isr_lock` and schedules `tasklet` when work is pending.
  - `brcms_dpc()` runs `brcms_c_dpc()`, handles reschedule logic, updates interrupt state, and wakes TX flush waiters.
- Common-driver callbacks and wrappers:
  - `brcms_init()`, `brcms_reset()`, `brcms_fatal_error()`, `brcms_intrson()`, `brcms_intrsoff()`, `brcms_intrsrestore()`, `brcms_up()`, `brcms_down()`, `brcms_txflowcontrol()`, and `brcms_rfkill_set_hw_state()`.
- Timer API:
  - `brcms_init_timer()`, `brcms_add_timer()`, `brcms_del_timer()`, `brcms_free_timer()`, and private `_brcms_timer()` wrap mac80211 delayed work with common-driver timer semantics.

## Control Flow
Module initialization calls `brcms_debugfs_init()` and schedules `brcms_driver_work`. The work item registers the BCMA driver. When BCMA probes a matching 802.11 core, `brcms_bcma_probe()` allocates an `ieee80211_hw` with `struct brcms_info` as private data, binds it to the BCMA device, and calls `brcms_attach()`.

Attach initializes synchronization, tasklet, waitqueue, common driver state, public pointers, IRQ, mac80211 capabilities, regulatory information, permanent MAC address, and debugfs. It then registers with mac80211 using `ieee80211_register_hw()`. After attach, the probe function attempts LED registration and returns success even if LED support is absent or fails.

The mac80211 start path lazily loads firmware if ucode data is not yet initialized, wakes queues, checks rfkill, mutes TX until a non-monitor interface is added, calls `brcms_up()` if unblocked, and enables PCI power save. Stop stops queues, verifies chip identity, disables PCI power save, and calls `brcms_down()`.

The TX callback takes `wl->lock`, drops packets if the driver is down, and otherwise passes the SKB to `brcms_c_sendpkt_mac80211()`. Configuration callbacks translate mac80211 changes into common-driver calls for listen interval, TX power, channel, retry limits, association, slot timing, HT protection, basic rates, beacon interval, BSSID, SSID, beacon/probe response templates, filters, scan state, WME TX parameters, TSF, and TIM updates. Several mac80211 notifications are logged as not implemented.

The interrupt path is split. `brcms_isr()` runs first-level common interrupt handling under `isr_lock` and schedules the tasklet. `brcms_dpc()` runs under `wl->lock`, optionally updates interrupt status under `isr_lock`, executes common deferred processing, reschedules itself if needed, otherwise re-enables interrupts, and wakes `tx_flush_wq` so `brcms_ops_flush()` can complete when common TX flush state is clear.

Timer calls from common code allocate `struct brcms_timer` wrappers backed by mac80211 delayed work. `_brcms_timer()` runs with `wl->lock`, handles periodic rescheduling, invokes the common callback, and maintains `wl->callbacks` so down/free paths can wait for callback completion.

Remove reverses probe: unregister LED, reset rfkill state and polling, unregister mac80211 hardware, release common/debug/firmware/timer/IRQ/tasklet resources through `brcms_free()`, clear BCMA drvdata, and free `ieee80211_hw`.

## State and Persistence
The central runtime state is `struct brcms_info` allocated as `hw->priv`. This file mutates `wl->pub`, `wl->wlc`, `irq`, `lock`, `isr_lock`, `tx_flush_wq`, `callbacks`, `timers`, `tasklet`, `resched`, firmware metadata, `wiphy`, ucode data, `mute_tx`, radio LED state, and LED class device state.

Global runtime state includes `n_adapters_found` and the scheduled `brcms_driver_work`. Channel/rate templates are static data copied into per-band common-driver storage at attach time. Firmware blobs are requested from userspace firmware storage at runtime, converted into `wl->ucode`, and then released; the copied ucode data remains until `brcms_free()`.

There is no driver-owned on-disk persistence. Regulatory hints, firmware files, and SPROM values are external inputs.

## Dependencies and Integration Points
- Linux subsystems: BCMA bus, mac80211, cfg80211/wiphy, firmware loader, interrupt API, tasklets, delayed work, wait queues, debugfs, rfkill, module init/exit, and LED support.
- Local brcmsmac common layer: `main.h`, `pub.h`, `scb.h`, `channel.h`, `ucode_loader.h`, `debug.h`, `led.h`, and many `brcms_c_*` functions.
- TX/RX integration is through `brcms_c_sendpkt_mac80211()`, `brcms_c_tx_flush_completed()`, AMPDU common helpers, and mac80211 queue control.
- Firmware integration uses `MODULE_FIRMWARE()` declarations, request/release firmware APIs, and the ucode loader callbacks declared in `ucode_loader.h`.
- Regulatory and hardware identity come from `wl->pub`, SROM country code, BCMA IDs, and PHY type reported by common code.

## Risks and Edge Cases
- `brcms_module_init()` registers the BCMA driver asynchronously. Module exit correctly cancels the work, but init can return success before registration has happened.
- Probe ignores the return value from `brcms_led_register()`, making LED setup optional but also easy to miss in automated validation.
- Many callbacks require `wl->lock`; some helpers intentionally drop and reacquire it, notably `brcms_rfkill_set_hw_state()` and `brcms_down()`. Locking regressions can create deadlocks or races with ISR/tasklet paths.
- `brcms_ops_start()` calls `bcma_core_pci_power_save(..., true)` even when `brcms_up()` returns an error, so failed starts still update PCI power-save state.
- Suspend currently only marks `wl->pub->hw_up = false`; resume is a no-op. Full suspend/resume behavior depends on other layers tolerating this minimal implementation.
- Several mac80211 features are logged as not implemented: power save changes, CQM details, IBSS join handling, ARP filtering, QoS notifications, and TX flow control.
- Firmware parsing depends on header/bin consistency and little-endian fields. `brcms_check_firmwares()` has validation logic, but callers must ensure it is run as part of ucode initialization.
- The timer free path waits for `callbacks` but uses scheduling/spin-wait patterns that can be sensitive to callback accounting bugs.
- `brcms_ops_sta_add()` uses a single primary SCB and sets a global AMPDU pointer, so multi-station behavior is limited.
- `brcms_ops_ampdu_action()` returns immediate TX BA start when aggregatable and flushes on stop; mistakes here affect mac80211/minstrel aggregation state.

## Test Signals
- Build tests with `CONFIG_BRCMSMAC`, `CONFIG_BRCMDBG`, `CONFIG_BRCMSMAC_LEDS`, and LED-disabled variants.
- Probe/remove tests on matching and non-matching BCMA core IDs, including allocation failure, common attach failure, IRQ request failure, invalid MAC address, hardware registration failure, and LED registration failure.
- Firmware tests for missing firmware, missing header, malformed header size, out-of-bounds sections, invalid section lengths, valid ucode buffer extraction, and valid 32-bit tag extraction.
- mac80211 functional tests for start/stop, STA/AP/ADHOC interface add/remove, TX while down, channel changes, TX power changes, retry limits, scan start/complete, filter changes, WME params, beacon/probe response updates, TSF get/set, and TIM update.
- AMPDU tests for STA add, TX start rejection when not aggregatable, operational transition, and all TX stop/flush actions.
- Interrupt tests should verify ISR schedules the tasklet, tasklet reschedules when common DPC requests it, interrupts are re-enabled when work completes, and flush waiters wake.
- Timer tests should cover one-shot timers, periodic timers, delete while pending/running, free while active, and unload with outstanding callbacks.
- rfkill tests should cover blocked start returning `-ERFKILL`, polling start/stop behavior, and hardware state updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/mac80211_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/mac80211_if.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/mac80211_if.h

## Purpose
`mac80211_if.h` declares the private Linux-interface types and cross-file callbacks for the `brcmsmac` mac80211 bridge. It defines the per-device `struct brcms_info`, timer wrapper type, firmware bookkeeping type, minimal interface wrapper, and the functions that common driver code calls back into the Linux integration layer.

## Important APIs, Types, and Functions
- `BRCMS_LEGACY_5G_RATE_OFFSET` marks where 5 GHz OFDM rates begin in the shared legacy rate table.
- `BRCMS_SET_SHORTSLOT_OVERRIDE` is a softmac ioctl definition used by surrounding code.
- `struct brcms_timer` wraps mac80211 delayed work and stores:
  - owning `struct brcms_info *wl`;
  - callback function and argument;
  - delay, periodic flag, active flag, and linked-list pointer for unload cleanup;
  - optional debug name.
- `struct brcms_if` contains a subunit and PCI device pointer for interface identity compatibility.
- `MAX_FW_IMAGES` is the firmware array bound.
- `struct brcms_firmware` stores requested firmware binaries, matching header blobs, header entry counts, and firmware count.
- `struct brcms_info` is the main per-device Linux-side object:
  - common/public pointers `pub` and `wlc`;
  - IRQ number and magic;
  - `lock` and `isr_lock`;
  - TX flush waitqueue;
  - callback accounting and timer list;
  - DPC tasklet and reschedule flag;
  - firmware/ucode/wiphy pointers;
  - `mute_tx`;
  - radio LED state and LED class device.
- Exported lifecycle and interrupt wrappers:
  - `brcms_init()`, `brcms_reset()`, `brcms_up()`, `brcms_down()`, `brcms_fatal_error()`.
  - `brcms_intrson()`, `brcms_intrsoff()`, and `brcms_intrsrestore()`.
  - `brcms_txflowcontrol()` and `brcms_rfkill_set_hw_state()`.
- Timer API:
  - `brcms_init_timer()`, `brcms_free_timer()`, `brcms_add_timer()`, `brcms_del_timer()`, `brcms_timer()` declaration, and `brcms_dpc()`.

## Control Flow
This header has no executable flow, but it defines the objects and callbacks used by the flow in `mac80211_if.c` and the common `brcms_c_*` code. Common code can allocate timers through `brcms_init_timer()`, start/stop hardware through `brcms_up()` and `brcms_down()`, control interrupts through `brcms_intrs*()`, and report fatal errors through `brcms_fatal_error()`.

`struct brcms_info` is allocated as the private tail of `struct ieee80211_hw`. Probe initializes it, mac80211 callbacks mutate it under locks, ISR/tasklet paths use it for synchronization and common-code dispatch, and remove/free tears it down.

## State and Persistence
The header defines runtime-only state. `struct brcms_info` persists for the lifetime of the registered hardware object. `struct brcms_firmware` holds firmware references only during request/ucode initialization, while `struct brcms_ucode` stores copied ucode data until detach. Timers are linked from `wl->timers` so unload can free them after callback completion.

## Dependencies and Integration Points
- Includes Linux timer, interrupt, workqueue, and LED headers for embedded delayed work, tasklet, waitqueue-adjacent state, and `struct led_classdev`.
- Includes local `ucode_loader.h` and `led.h`, making firmware and LED state part of the mac80211 interface object.
- `struct brcms_info` is shared by `mac80211_if.c`, `led.c`, common driver modules, timer users, interrupt handlers, and firmware loader code.
- The prototypes establish the Linux-side callback surface consumed by the common brcmsmac layer.

## Risks and Edge Cases
- Because `struct brcms_info` is broad shared state, changes to its fields can affect probe, mac80211 callbacks, timers, interrupts, firmware loading, and LED code simultaneously.
- The header exposes locking primitives but does not document per-function lock requirements beyond comments in the implementation. Callers must know which functions require the perimeter lock.
- `struct brcms_timer` callback accounting relies on correct `set` and `periodic` transitions; header users can misuse timer objects if they bypass the declared API.
- `MAX_FW_IMAGES` fixes firmware array bounds and must stay in sync with `brcms_firmwares[]` and module firmware declarations.
- The declaration `void brcms_timer(struct brcms_timer *t);` has no implementation in the reviewed `mac80211_if.c`, so references should be checked before use.

## Test Signals
- Compile tests should catch struct layout dependencies for `mac80211_if.c`, `led.c`, and common code.
- Timer API tests should verify callback accounting and linked-list cleanup using `struct brcms_timer`.
- Firmware tests should verify `MAX_FW_IMAGES` bounds against requested firmware names.
- Locking analysis should focus on functions declared here that are called from common code under the driver perimeter lock.
- Runtime probe/remove tests validate that all embedded fields in `struct brcms_info` are initialized before use and torn down in a safe order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/mac80211_if.h -->
