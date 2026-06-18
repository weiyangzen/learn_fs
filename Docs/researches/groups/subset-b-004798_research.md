# subset-b-004798 Research

Research item `subset-b-004798` covers Broadcom brcm80211 USB fullmac support, small fullmac helpers, WCC vendor plugin glue, and early brcmsmac softmac support files. Each section below is source-tree aligned and bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/usb.c

Purpose: implements the brcmfmac USB bus backend for Broadcom/Cypress FullMAC WLAN devices. It binds USB IDs, discovers bulk endpoints, identifies whether firmware is already running, downloads TRX firmware when required, exposes brcmf bus operations, and moves data/control packets between BCDC/core code and USB URBs.

Important APIs and types: `struct brcmf_usbdev_info` is the private bus state and must start with public `struct brcmf_usbdev`. It owns USB pipes, URB queues, control request state, firmware image metadata, flow-control watermarks, wait queue, and module settings. Bus entry points are `brcmf_usb_register()`, `brcmf_usb_exit()`, `brcmf_usb_probe()`, `brcmf_usb_disconnect()`, PM callbacks, and `brcmf_usb_bus_ops` (`preinit`, `stop`, `txdata`, `txctl`, `rxctl`, `get_blob`).

Control flow: probe validates USB class/interface, finds one bulk IN and one bulk OUT endpoint, allocates `devinfo`, and calls `brcmf_usb_probe_cb()`. Probe callback attaches request queues, creates a `brcmf_bus`, loads module parameters, checks `DL_GETVER`, and either attaches immediately for postboot firmware or requests firmware asynchronously. Phase 2 validates TRX headers, sends the image with bootloader commands (`DL_START`, bulk chunks, `DL_GO`, `DL_RESETCFG`), then calls `brcmf_alloc()` and `brcmf_attach()`. Runtime RX preposts URBs from `rx_freeq`; completions feed skb data to `brcmf_rx_frame()` and refill. Runtime TX dequeues `tx_freeq`, submits bulk URBs, reports completion through `brcmf_proto_bcdc_txcomplete()`, and toggles BCDC flow block around low/high watermarks.

State and persistence: all state is kernel memory and USB device state. Persistent external inputs are firmware files and module parameters. `bus_pub.state` transitions among DOWN, DL_FAIL, DL_DONE, UP, and SLEEP; upper bus state changes are forwarded through `brcmf_bus_change_state()`. The asynchronous firmware completion protects disconnect with `dev_init_done`.

Dependencies and integration: depends on Linux USB, firmware loader, skb allocation, brcmf core/bus/BCDC/firmware/common helpers, Broadcom chip IDs, and PM autosuspend. It integrates with cfg80211 indirectly after `brcmf_attach()`.

Risks and test signals: high-risk paths are async probe versus disconnect, URB queue accounting under spinlock, timeout cleanup of shared control URB, TRX length validation, reset-resume firmware reload, and flow-block release after TX completions. Useful signals are USB probe logs, firmware request/download errors, BCDC tx/rx counters, suspend/resume cycling, disconnect during firmware load, zero-length RX URBs, and queue exhaustion under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/usb.h

Purpose: declares the USB bus public state shared by `usb.c` and the rest of brcmfmac. It is intentionally compact and contains no implementation.

Important APIs and types: `enum brcmf_usb_state` defines the backend lifecycle states: DOWN, DL_FAIL, DL_DONE, UP, and SLEEP. `struct brcmf_stats` counts USB control packet successes and errors. `struct brcmf_usbdev` is the public bus object referenced from `struct brcmf_bus`; it stores back-pointers, current state, queue sizes, MTU, device/chip revision, and control statistics. `struct brcmf_usbreq` is the per-URB request wrapper used in free/post queues and carries a list node, URB, skb, and private bus pointer.

Control flow: this header participates in allocation and queue movement in `usb.c`; callers do not manipulate these fields directly except through the USB bus operations.

State and persistence: all fields are volatile kernel driver state. The only state that survives device reset is what can be rediscovered from USB descriptors and bootloader/chip IDs.

Dependencies and integration: depends on Linux list, URB, skb, and brcmf bus declarations included indirectly by C files. It forms the ABI boundary between brcmf bus core and the USB backend.

Risks and test signals: the key invariant is that `struct brcmf_usbdev_info` embeds `struct brcmf_usbdev` first, as required by `usb.c`. Queue misuse, stale skb pointers, or state transitions not matching `usb.c` expectations show up as URB leaks, flow-control stalls, or invalid bus state logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/vendor.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/vendor.c

Purpose: exposes a Broadcom cfg80211 vendor command that tunnels a firmware dongle command (`dcmd`) through nl80211 vendor command infrastructure.

Important APIs and functions: `brcmf_cfg80211_vndr_cmds_dcmd_handler()` is the sole handler. It parses `struct brcmf_vndr_dcmd_hdr`, obtains the `brcmf_if` from the wireless device, copies optional payload into a vmalloc buffer, calls `brcmf_fil_cmd_data_set()` or `brcmf_fil_cmd_data_get()`, and returns response data in one or more vendor reply skbs with `BRCMF_NLATTR_DATA` and `BRCMF_NLATTR_LEN`. `brcmf_vendor_cmds[]` registers subcommand `BRCMF_VNDR_CMDS_DCMD` under `BROADCOM_OUI`.

Control flow: input validation checks header length and payload offset, clamps input and return lengths to `BRCMF_DCMD_MAXLEN`, allocates `max(ret_len, len) + 1`, null terminates copied payloads, performs get/set, then chunks replies to `PAGE_SIZE - 0x100`.

State and persistence: no persistent state. It temporarily allocates `dcmd_buf` and reply skbs. Device-visible state may change when the vendor command is a set operation.

Dependencies and integration: depends on cfg80211 vendor command APIs, netlink attributes, brcmf cfg80211 VIF layout, and firmware interface (`fwil`). It is a userspace escape hatch into firmware command handling.

Risks and test signals: risks include malformed offsets, excessive lengths, firmware commands with mismatched set/get semantics, partial multi-skb replies, and exposing broad firmware controls to privileged userspace. Test with short headers, offset boundary cases, max-length input/output, failing firmware commands, and multi-page return buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/vendor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/vendor.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/vendor.h

Purpose: defines the Broadcom nl80211 vendor command identifiers, reply attributes, and command header used by `vendor.c`.

Important APIs and types: `BROADCOM_OUI` is `0x001018`. `enum brcmf_vndr_cmds` currently defines only `BRCMF_VNDR_CMDS_DCMD` besides unspecified/last markers. `enum brcmf_nlattrs` defines `BRCMF_NLATTR_LEN` and `BRCMF_NLATTR_DATA`. `struct brcmf_vndr_dcmd_hdr` contains firmware command id, expected return length, payload offset, get/set selector, and a magic field. `brcmf_vendor_cmds[]` is exported for cfg80211 registration.

Control flow: this header has no executable flow; it fixes the wire contract parsed by the vendor command handler.

State and persistence: no local state. Fields influence temporary command buffers and firmware state changes when userspace issues set commands.

Dependencies and integration: consumed by brcmfmac cfg80211 setup and `vendor.c`; externally, userspace tools must match this structure and attributes.

Risks and test signals: ABI drift would break userspace. The `magic` field is documented but not validated by the implementation, so tests should confirm current behavior rather than assume authentication. Attribute IDs and struct packing should be checked on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/vendor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/Makefile

Purpose: builds the WCC firmware-vendor plugin module for brcmfmac.

Important build objects: it adds include paths for the current directory, parent brcmfmac directory, and shared include directory. It builds `brcmfmac-wcc.o` as an external/module object from `core.o` and `module.o`.

Control flow: build-time only. The compiled module supplies vendor operations registered at module init.

State and persistence: no runtime state in the Makefile. Build outputs are kernel objects/modules controlled by Kbuild.

Dependencies and integration: depends on Kbuild variables and headers under brcmfmac and brcm80211 include paths. It integrates WCC as a separate object rather than folding it into the main brcmfmac module.

Risks and test signals: include path regressions or object list omissions cause module build failures or missing vendor registration. Test with `CONFIG_BRCMFMAC` module builds and ensure `brcmfmac-wcc.ko` exports the expected module metadata and imports namespace `BRCMFMAC` from `module.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/core.c

Purpose: implements WCC-specific brcmfmac firmware-vendor operations.

Important APIs and functions: `brcmf_wcc_set_sae_pwd()` maps SAE password setup to `brcmf_set_wsec()` using `BRCMF_WSEC_PASSPHRASE`. `brcmf_wcc_alloc_fweh_info()` allocates a flexible `struct brcmf_fweh_info` sized for `BRCMF_WCC_E_LAST` event handlers, initializes `num_event_codes`, and stores it on the driver. `brcmf_wcc_ops` exports these operations through the firmware-vendor abstraction.

Control flow: vendor registration in `module.c` publishes `brcmf_wcc_ops`; the brcmf core calls these hooks when handling SAE credentials and firmware event handler setup for WCC devices.

State and persistence: allocates `drvr->fweh` as kernel heap state tied to the brcmf driver lifetime. SAE password data comes from cfg80211 crypto settings and is sent to firmware rather than persisted here.

Dependencies and integration: depends on brcmf core, bus, fwvid, cfg80211, and flexible allocation helper `kzalloc_flex()`. It integrates with the generic vendor hook table `struct brcmf_fwvid_ops`.

Risks and test signals: event-code count must match firmware event IDs. Allocation failure should abort attach cleanly. SAE password length and lifetime should be validated by callers. Test WCC module load, driver attach, event dispatch setup, and WPA3 SAE connection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/module.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/module.c

Purpose: provides module lifecycle glue for the WCC brcmfmac firmware-vendor plugin.

Important APIs and functions: `brcmf_wcc_init()` registers `BRCMF_FWVENDOR_WCC`, `THIS_MODULE`, and `brcmf_wcc_ops` through `brcmf_fwvid_register_vendor()`. `brcmf_wcc_exit()` unregisters the same vendor. Module metadata describes the plugin, declares dual BSD/GPL licensing, imports namespace `BRCMFMAC`, and uses `module_init`/`module_exit`.

Control flow: when the module loads, the WCC vendor hooks become available to the main brcmfmac driver; unload removes them. The USB device table in `usb.c` sets many USB devices to `BRCMF_FWVENDOR_WCC`, so this registration is part of those devices' attach path.

State and persistence: module registration state lives in the brcmf fwvid registry. No per-device state is allocated here.

Dependencies and integration: depends on brcmf bus/core/fwvid APIs and the ops object from `core.c`. Integration failure prevents WCC-specific hooks from being resolved.

Risks and test signals: duplicate registration, unload while devices are active, or missing namespace exports can break module lifecycle. Test module load/unload, hotplug with WCC USB IDs, and unload refusal while referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/vops.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/vops.h

Purpose: declares the WCC firmware-vendor operations object for WCC plugin source files and consumers.

Important APIs and types: `extern const struct brcmf_fwvid_ops brcmf_wcc_ops;` is the single exported symbol declaration. `WCC_VOPS` is a convenience macro expanding to `&brcmf_wcc_ops`.

Control flow: no executable flow. It connects `core.c` implementation to `module.c` registration.

State and persistence: no state.

Dependencies and integration: depends on `struct brcmf_fwvid_ops` being visible to includers through their own includes. It is local plugin glue, not a public userspace interface.

Risks and test signals: mismatched declarations or missing include guards would cause build failures. Test by building the WCC module and checking that `module.c` links against `brcmf_wcc_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/vops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/xtlv.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/xtlv.c

Purpose: implements helpers for packing Broadcom extended TLV headers with configurable 8-bit or 16-bit id/length fields and optional 32-bit alignment.

Important APIs and functions: `brcmf_xtlv_data_size()` returns header plus data size, rounded to four bytes when `BRCMF_XTLV_OPTION_ALIGN32` is set. `brcmf_xtlv_pack_header()` writes id and length in little-endian or byte-sized forms according to `BRCMF_XTLV_OPTION_IDU8` and `BRCMF_XTLV_OPTION_LENU8`, then copies optional payload. Internal `brcmf_xtlv_header_size()` computes the variable header length from the nominal `struct brcmf_xtlv` layout.

Control flow: option combinations choose among 16/16, 8/8, 8/16, and 16/8 header layouts. Unexpected option combinations warn and return. Length is truncated to 8 bits after a warning when `LENU8` is set.

State and persistence: no persistent state. The caller owns the output buffer and must allocate enough space using the size helper.

Dependencies and integration: depends on Linux unaligned little-endian access, `roundup()`, and option definitions in `xtlv.h`. Used by brcmfmac firmware command/config payload builders.

Risks and test signals: caller buffer sizing is critical because pack does not receive buffer capacity. Data-size and pack-header option handling must agree. Test all four id/len width combinations, alignment rounding, null data payloads, and `LENU8` overflow warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/xtlv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/xtlv.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/xtlv.h

Purpose: defines the nominal XTLV structure and option flags for brcmfmac extended TLV serialization.

Important APIs and types: `struct brcmf_xtlv` is a 16-bit id, 16-bit length, flexible data layout used as the base layout even when options shrink fields. `enum brcmf_xtlv_option` defines 32-bit alignment, 8-bit id, and 8-bit length flags. The header declares `brcmf_xtlv_data_size()` and `brcmf_xtlv_pack_header()`.

Control flow: no executable flow. The option flags determine behavior in `xtlv.c`.

State and persistence: no state. Serialized data becomes part of firmware command buffers or other transport payloads.

Dependencies and integration: depends on Linux `types.h` and `bits.h`. It is a small helper interface for firmware-facing binary data.

Risks and test signals: because the struct is nominal, consumers must not assume `sizeof(struct brcmf_xtlv)` matches the wire header under all options. Tests should verify header bytes for every option combination and confirm alignment expectations against firmware consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/xtlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/Makefile

Purpose: Kbuild fragment for the Broadcom 802.11n SoftMAC driver module `brcmsmac`.

Important build objects: include paths cover the brcmsmac directory, `phy/`, and shared brcm80211 includes. `brcmsmac-y` composes the module from mac80211 interface, ucode loader, A-MPDU, antenna selection, channel/regulatory, main, PHY shim, PMU, rate, space-time formatting, AI utilities, PHY implementations/tables/qmath, DMA, trace events, and debug support. LED support is conditional on `CONFIG_BRCMSMAC_LEDS`; the module is selected by `CONFIG_BRCMSMAC`.

Control flow: build-time only. Runtime initialization is in the object files listed here.

State and persistence: no runtime state. Build outputs and configuration decide which features are present.

Dependencies and integration: integrates brcmsmac into Linux Kbuild and mac80211/cfg80211 driver stack.

Risks and test signals: missing object entries cause unresolved symbols or feature loss. Include path changes affect cross-file private headers. Test allmodconfig/module builds, `CONFIG_BRCMSMAC_LEDS` on/off, and trace/debug configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/aiutils.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/aiutils.c

Purpose: provides BCMA/AI chip utility support for brcmsmac, especially chipcommon discovery, clock-control setup, board/chip metadata access, and a 4313 external PA workaround.

Important APIs and functions: `ai_attach()` allocates `struct si_info` and calls `ai_doattach()` to populate public chip data from `bcma_bus`. `ai_detach()` frees it. `ai_cc_reg()` masks/sets chipcommon registers. `ai_clkctl_init()`, `ai_clkctl_fast_pwrup_delay()`, and `ai_clkctl_cc()` configure dynamic clock control and compute D11 fast wake delays. `ai_epa_4313war()` enables external PA GPIO control. `ai_deviceremoved()` checks PCI vendor ID disappearance.

Control flow: attach stores BCMA bus/PCI handles, chip ID/revision/package, board vendor/type, chipcommon revision/status/capabilities, PMU rev/caps, clears GPIO pullups/pulldowns, and measures ALP when PMU is present. Clock init uses chipcommon power-control capability, programs ILP divider to 1 MHz, then writes PLL/fref delay registers. Fast power-up delay uses PMU helper when available, otherwise derives a delay from slow-clock frequency and chipcommon registers.

State and persistence: `struct si_info` is heap state tied to driver lifetime. Hardware register writes persist until reset or later driver writes. No filesystem persistence.

Dependencies and integration: depends on Linux BCMA, PCI config access, chipcommon register offsets, PMU helpers, board/chip ID definitions, and brcmsmac public `si_pub` accessors.

Risks and test signals: incorrect clock delay math or capability detection can cause wake/PLL instability. `ai_deviceremoved()` only detects PCI-host removal. Test attach on supported BCMA chips, PMU and non-PMU paths, fast clock mode transitions, PCI hot removal, and 4313 EPA board behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/aiutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/aiutils.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/aiutils.h

Purpose: public header for brcmsmac AI/BCMA chip utility state, constants, and exported helper functions.

Important APIs and types: defines core sizes, maximum cores, DMA translation constants, chipcommon clock-control bits, GPIO conventions, and `struct si_pub` public chip metadata. `struct si_info` embeds `si_pub` first and adds BCMA bus, PCI bus, and chip status. Exports `ai_core_cflags()`, `ai_attach()`, `ai_detach()`, `ai_cc_reg()`, clock-control helpers, `ai_deviceremoved()`, and `ai_epa_4313war()`. Inline accessors return chip, board, PMU, and chipcommon fields.

Control flow: no implementation, but documents the handle model: callers obtain `si_pub` from attach, pass it to utility routines, and detach when done.

State and persistence: describes in-memory chip metadata and register manipulation APIs. Register writes through these helpers affect hardware state.

Dependencies and integration: depends on Linux BCMA and brcmsmac `types.h`. Used by main, PMU, PHY, and board setup code to avoid open-coding chipcommon access.

Risks and test signals: struct-first embedding is an ABI invariant for container conversions. Constants must match hardware documentation. Build tests catch declaration drift; runtime tests should validate chip metadata and clock behavior on each supported board family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/aiutils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ampdu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ampdu.c

Purpose: implements brcmsmac transmit A-MPDU aggregation policy, per-session header rewriting, block-ack status handling, retry decisions, and adaptive FIFO preloading to avoid TX underflows.

Important APIs and functions: `brcms_c_ampdu_attach()`/`detach()` create module state. `brcms_c_ampdu_reset_session()`, `brcms_c_ampdu_add_frame()`, and `brcms_c_ampdu_finalize()` build one aggregate from queued skbs. `brcms_c_ampdu_dotxstatus()` parses hardware status and completes/retries MPDUs. `brcms_c_ampdu_tx_operational()`, `brcms_c_ampdu_macaddr_upd()`, `brcms_c_ampdu_shm_upd()`, `brcms_c_aggregatable()`, and `brcms_c_ampdu_flush()` integrate with station, template RAM, SHM, and DMA.

Control flow: attach initializes per-TID enable masks, BA window sizes, retry limits, max RX factor, max TX length table by MCS/bandwidth/SGI, and FIFO preload tables. Adding frames enforces max frames/bytes, same priority, retry count selection, MCS-dependent aggregate length limits, and marks every MPDU as middle. Finalize fixes first/last MPDU flags, trims last delimiter/padding, updates PLCP lengths, AMPDU bits, mixed-mode lengths, RTS/CTS durations, fallback markers, and preload size. TX status builds BA bitmaps from multi-word hardware status, reports ACKed frames to mac80211, retransmits eligible misses, or completes failures.

State and persistence: `struct ampdu_info` holds policy and adaptive underflow state; `struct scb_ampdu` tracks station/TID retry and release limits. Hardware SHM/template RAM stores BA template address and watchdog/MIMO settings. No disk persistence.

Dependencies and integration: depends on mac80211 skb control blocks, D11 TX headers/status, DMA queues, rate helpers, antenna selection, PHY chanspec, shared memory offsets, and tracepoints.

Risks and test signals: high-risk areas are queue walking across aggregated DMA descriptors, BA bitmap indexing, retry accounting, endian updates in D11 headers, rate fallback PLCP handling, and underflow feedback. Test HT throughput, mixed priorities, fallback rates, RTS/CTS aggregates, tx underflow counters, BA timeout behavior, station teardown flush, and mac80211 tx status correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ampdu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ampdu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ampdu.h

Purpose: declares the brcmsmac A-MPDU session interface and module lifecycle functions.

Important APIs and types: `struct brcms_ampdu_session` carries the current aggregate builder state: `wlc`, skb queue, maximum aggregate length/frame count, current aggregate byte count, and DMA byte count. Exported functions reset a session, add frames, finalize an aggregate, attach/detach the AMPDU module, process TX status, update BA template MAC address, and update SHM.

Control flow: callers create/reset a session, repeatedly call `brcms_c_ampdu_add_frame()` until it returns `-ENOSPC` or input is exhausted, then call `brcms_c_ampdu_finalize()` before transmission.

State and persistence: session state is per aggregate and transient. Module state is hidden in `struct ampdu_info` from `ampdu.c`.

Dependencies and integration: depends on `struct brcms_c_info`, `struct scb`, `struct sk_buff`, and `struct tx_status` declarations from brcmsmac internals.

Risks and test signals: callers must not reuse a session without reset and must handle `-ENOSPC` by transmitting/finalizing the existing aggregate. Tests should validate single-frame and multi-frame aggregates, empty finalize, and TX status calls for both station-present and station-null cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ampdu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/antsel.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/antsel.c

Purpose: handles board-level MIMO antenna selection for brcmsmac, translating SROM/board configuration into ucode antenna pattern fields and per-frame antenna config IDs.

Important APIs and functions: `brcms_c_antsel_attach()` detects antenna switch type and availability from SROM and board flags, sets low-driver antenna type, and initializes default/current configs. `brcms_c_antsel_init()` writes default TX/RX antenna selection to SHM. `brcms_c_antsel_antcfg_get()` chooses default, configured, or auto-derived antenna configs for TX descriptors. `brcms_c_antsel_antsel2id()` converts ucode pattern back to selection ID. Internal conversion helpers map 2x3 and 2x4 board layouts through lookup tables.

Control flow: attach selects `ANTSEL_2x3`, `ANTSEL_2x4`, or not available based on `antswitch`, antenna availability, SROM revision, and `BFL2_2X4_DIV`. Init writes default TX and RX SHM fields. Per-frame lookup uses defaults unless caller requests explicit selection and auto mode is enabled.

State and persistence: `struct antsel_info` stores current/default configs, availability, type, and board switch value. Hardware SHM writes persist until reset or reconfiguration.

Dependencies and integration: depends on SSB SPROM data, brcms main/hardware APIs, PHY shim, SHM offsets in `d11.h`, and A-MPDU TX status using `brcms_c_antsel_antsel2id()`.

Risks and test signals: wrong table mapping causes poor RF performance or invalid antenna combinations. SROM edge cases fall back to no auto diversity. Test boards with 2x2, 2x3, and 2x4 layouts, default SHM values, per-frame auto fallback IDs, and invalid SROM configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/antsel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/antsel.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/antsel.h

Purpose: exposes the brcmsmac antenna selection module interface.

Important APIs: declares attach/detach, hardware init, antenna config retrieval, and conversion from ucode `mimo_antsel` pattern to antenna selection ID.

Control flow: main driver attaches the module during setup, calls init when programming hardware, asks for antenna configs when building TX descriptors, and detaches on shutdown.

State and persistence: hides `struct antsel_info` internals in `antsel.c`. Hardware state is SHM-programmed by implementation calls.

Dependencies and integration: depends on brcms internal types and board configuration parsed elsewhere. It is consumed by main TX/PHY/A-MPDU logic.

Risks and test signals: incorrect caller ordering, especially using config retrieval before attach/init, can produce default IDs or null dereferences. Build and runtime tests should cover no-antenna-selection boards and auto-selection capable boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/antsel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac.h

Purpose: defines brcmsmac core tracepoints for timers, deferred procedure calls, and MAC interrupt status.

Important APIs and tracepoints: `TRACE_EVENT(brcms_timer)` records timer milliseconds, set flag, and periodic flag. `TRACE_EVENT(brcms_dpc)` records DPC data pointer value. `TRACE_EVENT(brcms_macintstatus)` records device name, ISR context flag, interrupt status, and mask.

Control flow: when `CONFIG_BRCM_TRACING` is enabled, this header participates in tracepoint definition through `trace/define_trace.h`; otherwise stubs are provided by `brcms_trace_events.h`.

State and persistence: no driver state is owned. Trace events are transient kernel tracing records.

Dependencies and integration: depends on Linux tracepoint infrastructure and `struct brcms_timer` fields from mac80211 interface code. Included by aggregate trace header.

Risks and test signals: trace format changes affect tooling. `dev_name()` and timer fields must be valid at trace time. Test by enabling BRCM tracing and confirming timer/DPC/interrupt events appear under ftrace/perf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac_msg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac_msg.h

Purpose: defines tracepoints for brcmsmac log messages and debug messages.

Important APIs and tracepoints: `DECLARE_EVENT_CLASS(brcms_msg_event)` captures formatted `va_format` messages. `DEFINE_EVENT` creates `brcms_info`, `brcms_warn`, `brcms_err`, and `brcms_crit`. `TRACE_EVENT(brcms_dbg)` records debug level, function name, and formatted message. GCC diagnostics suppress format-suggestion warnings around trace macros.

Control flow: logging wrappers in `debug.c` emit normal device logs and then these tracepoints. When tracing is configured, `define_trace.h` materializes them.

State and persistence: no persistent state; trace buffers hold formatted message copies while tracing is active.

Dependencies and integration: depends on Linux tracepoint `__vstring` support and `struct va_format`. Integrated with brcms debug macros.

Risks and test signals: formatted varargs must remain valid for trace assignment inside the call. Test info/warn/err/crit and debug paths with tracing enabled and disabled, including dynamic debug levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac_tx.h

Purpose: defines TX-focused tracepoints for D11 descriptors, TX status words, and A-MPDU session summaries.

Important APIs and tracepoints: `brcms_txdesc` captures device name and a dynamic byte array copy of the TX descriptor. `brcms_txstatus` records frame length, frame ID, status, last TX time, sequence, PHY error, and ACK PHY RX status. `brcms_ampdu_session` records aggregate limits and current aggregate length/frame/DMA counts.

Control flow: A-MPDU and TX status code call these trace helpers while processing descriptors and completions. Tracepoint definitions are generated only under `CONFIG_BRCM_TRACING`; otherwise inline stubs are used.

State and persistence: no owned state. Trace records copy descriptor/status data at event time.

Dependencies and integration: depends on Linux tracepoints and brcmsmac TX paths. The dynamic descriptor array avoids depending on a single printable descriptor format.

Risks and test signals: large descriptor capture can increase trace overhead. Consumers need matching kernel trace format. Test with tracing enabled during TX traffic and A-MPDU aggregation, and verify disabled tracing compiles to stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_events.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_events.c

Purpose: creates the concrete brcmsmac tracepoint definitions in exactly one translation unit.

Important APIs and flow: includes `linux/module.h` for tracepoint infrastructure, skips body under sparse `__CHECKER__`, includes `mac80211_if.h`, defines `CREATE_TRACE_POINTS`, then includes `brcms_trace_events.h`.

Control flow: build-time tracepoint materialization only. Runtime tracepoint execution is driven by call sites in other files.

State and persistence: no driver runtime state.

Dependencies and integration: must be linked into `brcmsmac-y` so trace symbols exist when tracing is enabled. It aggregates the individual trace headers through `brcms_trace_events.h`.

Risks and test signals: defining `CREATE_TRACE_POINTS` in more than one file would duplicate symbols; omitting this object would leave tracepoints undefined. Test module builds with `CONFIG_BRCM_TRACING` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_events.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_events.h

Purpose: central trace include for brcmsmac, with no-op stubs when Broadcom tracing is disabled.

Important APIs and flow: includes basic Linux/device/tracepoint and `mac80211_if.h`. If `CONFIG_BRCM_TRACING` is not enabled, it redefines `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` to produce static inline no-op `trace_*` functions. It then includes core, TX, and message trace headers.

Control flow: compile-time selection between real tracepoints and no-op stubs.

State and persistence: no state.

Dependencies and integration: every brcmsmac source needing trace calls can include this header without sprinkling config guards around call sites.

Risks and test signals: stub macro signatures must match real tracepoint prototypes; otherwise disabled-tracing builds can pass while enabled builds fail or vice versa. Test both config modes and call sites using all trace families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/channel.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/channel.c

Purpose: implements brcmsmac channel/regulatory management, transmit-power limit construction, country/regdomain initialization, chanspec validation, and cfg80211 regulatory notifier behavior.

Important APIs and functions: `brcms_c_channel_mgr_attach()` creates `struct brcms_cm_info`, derives country/default regdomain from SROM alpha2, and applies initial country settings. `brcms_c_channel_set_chanspec()` computes regulatory power limits, applies local constraints, adjusts gmode for no-OFDM channels, and calls `brcms_b_set_chanspec()`. `brcms_c_channel_reg_limits()` fills `struct txpwr_limits` across CCK, OFDM, MCS, 20/40 MHz, SISO/CDD/STBC/MIMO tables. `brcms_c_valid_chanspec_db()` validates chanspec shape/band. `brcms_c_regd_init()` masks unsupported PHY channels, installs notifier, applies custom regulatory domain, and relaxes beaconing flags where allowed.

Control flow: attach chooses `X2` default when SROM country is invalid or not in the small local table. Setting a channel reads cfg80211 current channel flags and local constraints, clamps every power table entry, and programs hardware. Regulatory notifier reapplies radar/no-IR rules, checks if any channel remains legal, toggles radio country-disable bit, and adjusts Japan channel 14 widefilter behavior.

State and persistence: `brcms_cm_info` stores current world regdomain pointer and driver references. cfg80211 channel flags and hardware tx power/channel state persist until later regulatory/channel changes or reset.

Dependencies and integration: depends on cfg80211/mac80211 regulatory APIs, PHY channel capability queries, brcms main/STF/gmode/hardware programming, SSB SPROM alpha2, and power constants from `channel.h`.

Risks and test signals: regulatory correctness is high risk. The local country table is minimal, power table indexing must match 2.4/5 GHz channel groups, and zero-as-unspecified fallback behavior must not create illegal power. Test valid/invalid alpha2 values, DFS/no-IR behavior, country IE notifier paths, all-disabled-channel radio disable, channel 14 Japan handling, and 20/40 MHz power limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/channel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/channel.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/channel.h

Purpose: declares brcmsmac channel manager APIs and regulatory power flag constants.

Important APIs and constants: `BRCMS_TXPWR_DB_FACTOR` converts dB to quarter-dB units. Locale flags describe peak/EIRP/DFS/no-OFDM/no-40MHz/no-MIMO/radar policy. Exports channel manager attach/detach, chanspec validation, regulatory limit calculation, chanspec setting, and regulatory initialization.

Control flow: no implementation, but callers use attach during driver setup, call `brcms_c_regd_init()` after wiphy/channel tables exist, validate chanspecs before programming, and call set/reg-limits during channel changes.

State and persistence: hides `struct brcms_cm_info` implementation. Hardware and cfg80211 state are changed by the functions declared here.

Dependencies and integration: used by brcmsmac main and PHY/channel programming code; interacts with `struct txpwr_limits`.

Risks and test signals: unit conversion mistakes at call sites can over/under-limit transmit power. Tests should compare expected qdBm values and validate that callers handle false chanspec validation results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/channel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/d11.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/d11.h

Purpose: defines the D11 MAC/PHY hardware register layout, descriptor/status wire formats, shared-memory offsets, and bit fields used throughout brcmsmac.

Important APIs and types: `struct d11regs` maps D11 core registers, including interrupt controls, MAC control/status, template access, PMQ, DMA/PIO FIFOs, PHY/radio access, TX/RX/TSF/IFS/WEP/SHM blocks. `D11REGOFFS()` computes offsets. `struct d11txh`, `struct tx_status`, `struct d11rxhdr_le`, `struct d11rxhdr`, `struct macstat`, and `struct d11cnt` define DMA headers, TX status packets, RX headers, ucode counters, and public counters. Numerous macros define TX control, PLCP, A-MPDU, security, RX status, SHM, host flags, FIFO, PHY, and interrupt bits.

Control flow: no executable flow. Runtime code reads/writes these offsets through BCMA and brcms_b helpers, and interprets DMA headers/status using the packed structures and masks.

State and persistence: this header describes volatile MMIO, template RAM, and ucode shared memory state. Writes affect hardware operation until reset or later programming.

Dependencies and integration: depends on IEEE80211, brcms `pub.h`, and DMA register definitions. It is central to `main.c`, `dma.c`, `ampdu.c`, `antsel.c`, `debug.c`, PHY code, and hardware bring-up.

Risks and test signals: any incorrect offset, endianness, packing, or bit mask can corrupt hardware programming. High-risk structures are `d11regs`, `d11txh`, RX/TX status formats, and SHM offsets used by ucode. Test signals include hardware init success, interrupts, TX/RX traffic, security key install, A-MPDU operation, debugfs macstat values, and sparse/compile checks for packed unaligned access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/d11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/debug.c

Purpose: provides brcmsmac debugfs files and logging wrappers that also emit tracepoints.

Important APIs and functions: `brcms_debugfs_init()`/`exit()` create/remove the module root. `brcms_debugfs_attach()`/`detach()` create/remove per-device debugfs directories. `brcms_debugfs_create_files()` adds `hardware` and `macstat` read-only files. `brcms_debugfs_hardware_read()` prints chip, board, ucode, radio, PHY, and NVRAM metadata. `brcms_debugfs_macstat_read()` snapshots and prints many ucode MAC counters. The `__brcms_info/warn/err/crit` wrappers call device logging and tracepoints; `__brcms_dbg()` conditionally emits debug logs and trace events.

Control flow: attach creates directory, create-files allocates `brcms_debugfs_entry` with device-managed memory and binds `single_open()` seq readers. `macstat` takes `wl->lock` while copying the snapshot, then prints without holding the lock.

State and persistence: debugfs dentries exist while module/device is active. Entries reference driver state but do not persist data. Trace/log records are transient.

Dependencies and integration: depends on debugfs, seq_file, mac80211 private state, D11/macstat definitions, Broadcom utility formatting, and trace events.

Risks and test signals: readers must not dereference freed driver state after detach; debugfs removal ordering matters. Macstat snapshot locking must match writers. Test mounting debugfs, reading hardware/macstat during traffic, device detach while readers exist, and tracing/debug-level combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/debug.h

Purpose: declares brcmsmac logging/debugfs APIs and convenience macros for categorized debug output.

Important APIs and macros: declares `__brcms_info()`, `__brcms_warn()`, `__brcms_err()`, `__brcms_crit()`, optional `__brcms_dbg()`, debugfs lifecycle/create functions, and macros that bind a `bcma_device` core to device logging. Category helpers cover info, mac80211, rx, tx, interrupt, DMA, and HT debug levels.

Control flow: when neither `CONFIG_BRCMDBG` nor `CONFIG_BRCM_TRACING` is enabled, `__brcms_dbg()` is an inline no-op. Other log wrappers always exist.

State and persistence: no state. Macros route runtime logs and trace events implemented in `debug.c`.

Dependencies and integration: depends on Linux device, BCMA, cfg80211/mac80211, and brcms main/mac80211 interface headers. Included by many brcmsmac implementation files.

Risks and test signals: debug macros assume a fully initialized `wlc`/core and the file explicitly warns against use before `brcms_c_attach()` succeeds. Tests should build all debug/tracing config combinations and exercise log paths before and after attach only where valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/debug.h -->
