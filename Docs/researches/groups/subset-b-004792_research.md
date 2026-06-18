# Research Group: subset-b-004792

This grouped report covers Broadcom b43/b43legacy wireless driver files from the Ceph client source snapshot. Each section is bounded with reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/xmit.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/xmit.c

## Purpose
Implements modern `b43` transmit and receive framing helpers. It translates mac80211 TX metadata into Broadcom firmware TX headers, decodes RX firmware headers into `ieee80211_rx_status`, parses PLCP rate information, maps encryption key indexes between raw and firmware formats, and routes TX completion to either DMA or PIO backends.

## Important APIs, Types, and Functions
Key exported functions are `b43_generate_txhdr`, `b43_generate_plcp_hdr`, `b43_rx`, `b43_handle_txstatus`, `b43_fill_txstatus_report`, `b43_tx_suspend`, and `b43_tx_resume`. Internal helpers include CCK/OFDM PLCP rate-code conversion, `b43_generate_tx_phy_ctl1`, `b43_calc_fallback_rate`, and `b43_rssi_postprocess`. It depends on `struct b43_txhdr`, `struct b43_rxhdr_fw4`, `struct b43_txstatus`, and key-index helpers declared in `xmit.h`.

## Control Flow
TX starts in `b43_generate_txhdr`: choose the main and fallback rates from mac80211, populate PLCP and PHY/MAC control words, copy receiver address and frame control, optionally attach hardware crypto metadata, generate RTS/CTS templates, encode firmware-format cookie fields for the active firmware header layout, and return an error only for invalid/missing keys or mapping assumptions. RX starts in `b43_rx`: decode status fields based on firmware header format, reject decrypt errors and undersized frames, remove PLCP/padding, calculate signal and rate index, fill band/frequency/timestamp metadata, and deliver the skb with `ieee80211_rx_ni`. TX status handling logs debugfs state, updates dot11 counters, dispatches to PIO or DMA completion, and triggers a TX power check.

## State and Persistence
The file does not persist data on disk. It mutates live driver and mac80211 state: `dev->wl->ieee_stats`, per-key state in `dev->key`, RX counters under debug builds, skb control blocks, and mac80211 TX retry status arrays. Firmware revision and header-format state controls which union fields are read or written.

## Dependencies and Integration Points
Integrates with mac80211 (`ieee80211_get_tx_rate`, RTS/CTS generation, RX/TX status APIs), b43 PHY helpers, b43 DMA/PIO backends, firmware header contracts, and Linux skb handling. Hardware crypto integration depends on mac80211 key configuration and b43 key-table semantics.

## Risks
The code contains several firmware-version assumptions: header-format unions, key-index API transition around firmware revision 351, and G-PHY channel encoding before/after firmware 508. Missing key configuration intentionally drops encrypted frames to avoid plaintext leaks. RX timestamp reconstruction assumes processing within roughly 65 ms of the received mactime. Rate table ordering must stay synchronized with mac80211 band tables.

## Test Signals
Useful signals are successful association and traffic over CCK/OFDM rates, encrypted TX with WEP/TKIP/AES keys, RTS/CTS protection traffic, monitor-mode radiotap timestamps, FCS/PLCP failure counters under injected bad frames, and correct TX retry accounting from rate-control traces. Suspend/resume should not transmit encrypted frames before keys are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/xmit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/xmit.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/xmit.h

## Purpose
Defines the modern `b43` transmit/receive firmware data structures and bitfields consumed by `xmit.c`, DMA, and PIO code. It documents the packed TX header layouts for multiple v4 firmware formats, RX metadata layout, TX status report format, PLCP headers, security key-index conversion helpers, and the driver-private mac80211 TX metadata storage.

## Important APIs, Types, and Functions
Important types are `struct b43_plcp_hdr4`, `struct b43_plcp_hdr6`, `struct b43_txhdr`, `struct b43_tx_legacy_rate_phy_ctl_entry`, `struct b43_txstatus`, `struct b43_rxhdr_fw4`, and `struct b43_private_tx_info`. Important inline helpers are `b43_txhdr_size`, `b43_new_kidx_api`, `b43_kidx_to_fw`, `b43_kidx_to_raw`, and `b43_get_priv_tx_info`. The file exports prototypes for TX header generation, PLCP generation, RX delivery, TX status handling, and TX suspend/resume.

## Control Flow
This header has no runtime control flow beyond inline helpers. Consumers select a TX header size from `dev->fw.hdr_format`, write fields into one of the packed firmware-format union members, and use bit masks to build MAC/PHY control words. RX code reads the packed firmware header and decodes PHY/MAC/channel bitfields into mac80211 status. Key-index helpers convert indexes at the boundary between mac80211-visible raw key slots and firmware-specific key numbering.

## State and Persistence
The declarations describe volatile firmware-facing memory and skb control metadata only. No persistent state exists here. The packed layout is itself a persistence-like ABI contract with the firmware and DMA/PIO descriptor code: padding and field sizes must remain stable.

## Dependencies and Integration Points
Depends on `main.h`, Linux packed integer types, and mac80211. It is used by `xmit.c`, DMA/PIO transmit paths, debugfs TX status logging, and any code that needs to size or decode b43 firmware headers.

## Risks
Packed layout drift can break firmware communication silently. The key-index conversion has a documented uncertainty about the exact revision where the API changed. `b43_txhdr_size` must stay consistent with `struct b43_txhdr` union layouts and supported firmware revisions. Rate and PHY bit definitions must remain aligned with firmware expectations, not merely compiler layout.

## Test Signals
Compile-time structure-size checks, successful TX on firmware formats 351/410/598, key-index correctness with default and per-station keys, and RX metadata sanity across CCK/OFDM/N/HT PHYs are the primary signals. DMA/PIO smoke tests should catch incorrect TX header sizes through failed transmission or bad cookies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/xmit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/Kconfig

## Purpose
Defines kernel configuration options for the legacy Broadcom 43xx mac80211 driver. It controls whether `b43legacy` builds, which SSB host glue is auto-selected, optional LED and hardware RNG integration, debug support, and whether DMA, PIO, or both transfer backends are compiled.

## Important APIs, Types, and Functions
The top-level symbol is `B43LEGACY`, a tristate depending on `SSB_POSSIBLE`, `MAC80211`, and `HAS_DMA`, selecting `SSB` and `FW_LOADER`. Helper symbols include `B43LEGACY_PCI_AUTOSELECT`, `B43LEGACY_PCICORE_AUTOSELECT`, `B43LEGACY_LEDS`, `B43LEGACY_HWRNG`, `B43LEGACY_DEBUG`, `B43LEGACY_DMA`, and `B43LEGACY_PIO`. The transfer-mode choice selects `B43LEGACY_DMA_AND_PIO_MODE`, `B43LEGACY_DMA_MODE`, or `B43LEGACY_PIO_MODE`.

## Control Flow
Kconfig selection determines compile-time code paths. If both DMA and PIO are compiled, runtime module parameter `pio` can choose PIO; otherwise inline stubs and `b43legacy_using_pio` collapse to the compiled backend. LED and debugfs code are conditionally compiled through their respective config symbols. PCI SSB bridge symbols are auto-selected only when their platform support is possible.

## State and Persistence
Kconfig state persists in kernel build configuration, not driver runtime. It shapes module features, available module parameters, and whether optional state objects such as LED class devices, debugfs entries, or hwrng registration exist.

## Dependencies and Integration Points
Integrates with the kernel build system, SSB bus support, firmware loader, mac80211, LED class/mac80211 LED trigger support, and hwrng. Help text also documents the external requirement for V3 firmware installed with b43-fwcutter.

## Risks
Misconfigured transfer mode can omit the only working data path for a device. PIO-only builds are slower and may not support all devices. `B43LEGACY_DEBUG` defaults to enabled, which improves diagnostics but increases code and logging surface. Firmware absence is not represented as a build dependency and only fails at runtime.

## Test Signals
Build matrix coverage for module/built-in states, DMA-only, PIO-only, DMA+PIO, LED-enabled/disabled, debugfs-enabled/disabled, and hwrng-enabled/disabled is the main signal. Runtime probing should confirm both `b43` and `b43legacy` can coexist and SSB loads the appropriate driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/Makefile

## Purpose
Builds the `b43legacy` composite kernel object from its core and optional feature modules. It maps Kconfig symbols to object inclusion and registers `b43legacy.o` under `CONFIG_B43LEGACY`.

## Important APIs, Types, and Functions
The base object list includes `main.o`, `ilt.o`, `phy.o`, `radio.o`, `sysfs.o`, `xmit.o`, and `rfkill.o`. Optional objects are `leds.o` for `CONFIG_B43LEGACY_LEDS`, `debugfs.o` for `CONFIG_B43LEGACY_DEBUG`, `dma.o` for `CONFIG_B43LEGACY_DMA`, and `pio.o` for `CONFIG_B43LEGACY_PIO`. The final line adds `b43legacy.o` to `obj-$(CONFIG_B43LEGACY)`.

## Control Flow
There is no runtime control flow. Build-time control determines which translation units are linked into the module or built-in driver. Header stubs in optional components must match these object selections so disabled features still compile cleanly.

## State and Persistence
The file influences build artifacts only. It does not create runtime state, but it determines whether runtime state for DMA rings, PIO queues, LEDs, debugfs entries, and debug logs can exist.

## Dependencies and Integration Points
Integrates with the Linux kbuild composite-object convention. The listed objects correspond to the driver subsystems consumed by `main.c`: firmware/core lifecycle, PHY/radio calibration, sysfs, transmit formatting, rfkill, LEDs, debugfs, DMA, and PIO.

## Risks
Object omissions or Kconfig mismatches can produce link failures or runtime stubs that hide missing functionality. Because `main.o` calls both DMA and PIO APIs through compile-time stubs, the Makefile and headers must remain synchronized with Kconfig.

## Test Signals
Kernel builds under each transfer-mode choice and optional feature combination are sufficient. A useful guard is checking that disabling debug or LEDs removes the object while preserving successful compilation through inline stub APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/b43legacy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/b43legacy.h

## Purpose
Central private header for the legacy Broadcom 43xx driver. It defines MMIO offsets, SHM routing constants, host flags, IRQ masks, rate constants, firmware file formats, PHY/radio state, DMA/PIO container state, shared mac80211 device state, per-core device state, locking rules, low-level SSB accessors, and logging prototypes.

## Important APIs, Types, and Functions
Important structures are `b43legacy_wl` for chip-wide mac80211 state, `b43legacy_wldev` for one SSB 802.11 core, `b43legacy_phy`, `b43legacy_dma`, `b43legacy_pio`, `b43legacy_firmware`, `b43legacy_key`, `b43legacy_noise_calculation`, and `b43legacy_stats`. Firmware ABI types are `b43legacy_fw_header` and `b43legacy_iv`. Inline helpers include `hw_to_b43legacy_wl`, `dev_to_b43legacy_wldev`, `b43legacy_using_pio`, `b43legacy_is_mode`, MMIO read/write wrappers, `b43legacy_get_lopair`, and board-vendor checks.

## Control Flow
The header establishes state-machine and locking contracts rather than implementing major flow. `b43legacy_status` and `b43legacy_set_status` wrap the atomic initialization state transitions among uninitialized, initialized, and started. `b43legacy_using_pio` compiles to runtime or constant selection depending on Kconfig. MMIO helpers route all register access through SSB read/write primitives.

## State and Persistence
All defined state is live kernel driver state. Persistent hardware/firmware-facing state includes SHM offsets, key-table pointers, GPIO/radio bits, firmware references, calibration tables, and rate tables stored in device memory. The lock policy states that `wl->mutex` and `wl->irq_lock` usually protect core state, with exceptions for IRQ, tasklet, and packet TX paths.

## Dependencies and Integration Points
Depends on Linux kernel primitives, SSB, mac80211, debugfs/LED/rfkill/PHY headers, hwrng, netdevice, PCI, and atomic/spinlock APIs. It is consumed by nearly every b43legacy source file.

## Risks
Changing constants can break undocumented firmware/hardware ABI. The shared `union` of DMA and PIO state assumes only one backend is active. Lock-order mistakes around `wl->mutex` and `irq_lock` can deadlock IRQ/tasklet/workqueue paths. Structure fields are widely shared, so small changes have high blast radius.

## Test Signals
Compile coverage across config variants, sparse/lockdep runs, probe/init/start/stop cycles, suspend/resume, RF-kill transitions, and mixed DMA/PIO builds validate this header. Hardware smoke tests are essential because many constants are only validated by device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/b43legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/debugfs.c

## Purpose
Implements optional debugfs support for inspecting and controlling a live b43legacy device. It exposes TSF read/write, ucode register dumps, shared-memory dumps, TX status history, manual restart, and dynamic debug booleans.

## Important APIs, Types, and Functions
Public functions are `b43legacy_debugfs_init`, `b43legacy_debugfs_exit`, `b43legacy_debugfs_add_device`, `b43legacy_debugfs_remove_device`, `b43legacy_debugfs_log_txstat`, and `b43legacy_debug`. Internal file handlers include `tsf_read_file`, `tsf_write_file`, `ucode_regs_read_file`, `shm_read_file`, `txstat_read_file`, and `restart_write_file`. `struct b43legacy_debugfs_fops` binds read/write callbacks to fields inside `struct b43legacy_dfsentry`.

## Control Flow
Module init creates a root debugfs directory. Per-device attach allocates a dfs entry, allocates a circular TX status log, creates files under a wiphy-named directory, and registers dynamic debug booleans. Generic debugfs read allocates a 16 KiB buffer on first read, optionally takes `wl->irq_lock`, calls the selected read callback, serves data with `simple_read_from_buffer`, and frees the buffer when fully consumed. Writes copy at most one page from userspace, optionally take `irq_lock`, and call the selected writer.

## State and Persistence
Debugfs state is runtime-only. `dev->dfsentry` owns per-file buffers, dynamic debug booleans, and a 100-entry TX status circular log protected by its own spinlock. TSF writes and restart writes mutate hardware state. Debugfs files are not persistent across module unload or device detach.

## Dependencies and Integration Points
Uses Linux debugfs, file operations, mutexes, spinlocks, page allocation, and copy-to/from-user helpers. It calls main-device helpers for TSF, SHM, restart, DMA/PIO debug flags, and TX status structures from xmit.

## Risks
Debugfs read buffers are per-file-entry and must be freed after EOF; interrupted reads can retain temporary pages until the next full read or detach. `shm_read_file` dumps a fixed 0x1000 words bounded by the 16 KiB buffer. Manual restart can race with device teardown unless status and locks are respected. The TX status logger expects IRQs disabled when called.

## Test Signals
With `CONFIG_B43LEGACY_DEBUG`, verify debugfs directory creation/removal, successful reads of `tsf`, `ucode_regs`, `shm`, `txstat`, TSF writes, restart writes with `1`, dynamic debug toggles, and detach after partial reads. Lockdep and KASAN are useful for buffer lifetime and locking issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/debugfs.h

## Purpose
Declares the optional b43legacy debugfs interface and provides no-op stubs when debug support is disabled. It centralizes dynamic debug feature IDs, per-device debugfs state layout, and TX status log structures.

## Important APIs, Types, and Functions
`enum b43legacy_dyndbg` defines dynamic toggles for transmit power, DMA overflow injection, DMA verbosity, fast periodic work, and periodic-work stop. Under `CONFIG_B43LEGACY_DEBUG`, the header defines `B43legacy_NR_LOGGED_TXSTATUS`, `struct b43legacy_txstatus_log`, `struct b43legacy_dfs_file`, and `struct b43legacy_dfsentry`. It declares `b43legacy_debug`, debugfs lifecycle functions, per-device add/remove functions, and TX status logging.

## Control Flow
The enabled path lets callers query runtime booleans and log TX statuses. The disabled path compiles all functions to harmless inline stubs and `b43legacy_debug` to false, allowing main, DMA, and xmit code to call debug helpers unconditionally.

## State and Persistence
The enabled structures hold runtime-only debugfs dentries, cached read buffers, dynamic booleans, and a TX status ring. Disabled builds reduce `struct b43legacy_led`-style debug state to nothing outside fields conditionally embedded in `b43legacy_wldev`.

## Dependencies and Integration Points
Forward-declares `b43legacy_wldev`, `b43legacy_txstatus`, and `dentry` to avoid heavy includes. It integrates with `b43legacy.h`, `debugfs.c`, DMA overflow testing, periodic work behavior, and TX status logging from xmit paths.

## Risks
The debug enum order indexes a boolean array and must stay aligned with `debugfs.c` creation order. Stub behavior can hide code paths that are only built in debug configurations, so both debug and non-debug builds need coverage. Buffer fields in `b43legacy_dfsentry` reflect files that are partly historical; implementation and structure must remain compatible.

## Test Signals
Build with and without `CONFIG_B43LEGACY_DEBUG`. Enabled builds should expose all dynamic booleans and debug files; disabled builds should eliminate debugfs dependencies while preserving successful linkage of callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/dma.c

## Purpose
Implements b43legacy DMA ring allocation, controller setup/reset, TX descriptor submission, TX status completion, RX buffer recycling, DMA error handling support, and queue suspend/resume. It is the high-throughput transfer backend selected unless PIO is forced or DMA mask setup fails.

## Important APIs, Types, and Functions
Public APIs are `b43legacy_dma_init`, `b43legacy_dma_free`, `b43legacy_dma_tx`, `b43legacy_dma_handle_txstatus`, `b43legacy_dma_rx`, `b43legacy_dma_tx_suspend`, and `b43legacy_dma_tx_resume`. Important internal helpers include `op32_fill_descriptor`, `request_slot`, `b43legacy_dmacontroller_rx_reset`, `b43legacy_dmacontroller_tx_reset`, `b43legacy_dma_mapping_error`, `setup_rx_descbuffer`, `dmacontroller_setup`, `b43legacy_setup_dmaring`, `generate_cookie`, `parse_cookie`, and `dma_tx_fragment`.

## Control Flow
Initialization probes 30-bit versus 32-bit address-extension support, sets DMA masks, obtains SSB translation bits, creates six TX rings and one or two RX rings, allocates coherent descriptor pages, preallocates RX skbs, and enables controller registers. TX maps each skb into two descriptors: a cached firmware TX header descriptor and a payload descriptor, with bounce-buffer fallback for unsupported DMA addresses. When free slots fall below two descriptors, the corresponding mac80211 queue is stopped. TX status parses the cookie back to ring/slot, validates in-order completion, unmaps descriptors, fills mac80211 retry/ACK status, frees ownership via `ieee80211_tx_status_irqsafe`, updates ring counters, and wakes queues/work. RX walks from software `current_slot` to hardware slot, handles RX-ring 3 TX-status packets on older cores, swaps in a fresh skb before unmapping the completed one, strips frame offset, and calls `b43legacy_rx`.

## State and Persistence
State is in `struct b43legacy_dmaring`: coherent descriptor memory, metadata array, TX header cache, DMA base, current/used slots, stopped flags, queue priority, and debug high-water marks. DMA mappings persist only until completion or ring teardown. RX descriptors persist for the ring lifetime and are recycled.

## Dependencies and Integration Points
Depends on Linux DMA mapping APIs, SSB DMA translation, skb allocation, mac80211 queue/status APIs, b43legacy xmit header generation, debugfs dynamic toggles, and main IRQ dispatch. It integrates with `b43legacy_wldev->dma` and `b43legacy_using_pio` fallback logic.

## Risks
The current `priority_to_txring` returns `tx_ring1` unconditionally before its detailed mapping, so queue priority/ring-priority behavior is effectively disabled. TX completion assumes in-order status per ring; out-of-order firmware reports can leak descriptors and stall DMA. Mapping failure rollback must restore ring counters exactly. RX buffer replacement failure drops frames but must keep descriptor ownership coherent. Queue wake logic around `tx_queue_stopped` is subtle.

## Test Signals
Exercise sustained TX/RX, DMA mask fallback to PIO, queue stop/wake under ring pressure, debug DMA overflow injection, RX on both ring 0 and ring 3 for older cores, encrypted TX drops with missing keys, suspend/resume DMA suspend, and module unload after traffic. DMA API debug and lockdep are valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/dma.h

## Purpose
Declares the b43legacy DMA backend register definitions, descriptor layout, ring constants, metadata structures, inline MMIO accessors, public DMA APIs, and stubs for non-DMA builds.

## Important APIs, Types, and Functions
Defines DMA IRQ masks, 32-bit DMA controller register offsets and bitfields, `struct b43legacy_dmadesc32`, descriptor control flags, ring sizes, RX buffer sizes, `struct b43legacy_dmadesc_meta`, `enum b43legacy_dmatype`, and `struct b43legacy_dmaring`. Inline helpers `b43legacy_dma_read` and `b43legacy_dma_write` access controller registers. Public prototypes mirror `dma.c`.

## Control Flow
Enabled builds provide real DMA functions. Disabled builds return success/no-op for init/free/status/rx/suspend/resume and a benign zero from `b43legacy_dma_tx`, allowing the rest of the driver to compile when only PIO is selected. Runtime code uses `b43legacy_using_pio` to avoid real DMA calls when PIO is active.

## State and Persistence
The ring structure describes persistent runtime DMA state: descriptor memory, metadata, cached TX headers, DMA addresses, slot counters, frame offsets, controller index, backend type, stopped state, queue priority, and debug counters. Hardware-visible descriptors are packed ABI data shared with the DMA engine.

## Dependencies and Integration Points
Depends on `b43legacy.h`, kernel list/spinlock/workqueue/atomic headers, DMA address types, and mac80211/skb forward declarations. It is consumed by `main.c`, `dma.c`, debugfs, and transfer-mode selection code.

## Risks
Incorrect bit masks or descriptor packing can corrupt DMA. Ring constants must match controller expectations and RX frame sizes. Stub behavior in non-DMA builds means callers must not rely on DMA side effects unless DMA is compiled and selected. `queue_prio` must be initialized consistently with mac80211 queue mapping.

## Test Signals
Compile DMA-enabled and PIO-only configs, verify descriptor size and packed layout, run DMA API debug, and test TX/RX on hardware requiring 30-bit and 32-bit DMA masks. Queue stop/wake and unload-after-traffic are core validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/ilt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/ilt.c

## Purpose
Provides initial internal lookup-table data for b43legacy PHY/radio calibration and helper functions to read/write device ILT entries. Tables include rotor, retard, fine-frequency, noise, noise-scale, and sigma-square values used by PHY calibration code.

## Important APIs, Types, and Functions
Exports constant arrays declared in `ilt.h`: `b43legacy_ilt_rotor`, `b43legacy_ilt_retard`, `b43legacy_ilt_finefreqa`, `b43legacy_ilt_finefreqg`, `b43legacy_ilt_noisea2`, `b43legacy_ilt_noisea3`, `b43legacy_ilt_noiseg1`, `b43legacy_ilt_noiseg2`, `b43legacy_ilt_noisescaleg1/2/3`, and `b43legacy_ilt_sigmasqr1/2`. Public helpers are `b43legacy_ilt_write`, `b43legacy_ilt_write32`, and `b43legacy_ilt_read`.

## Control Flow
Most of the file is static calibration data. Access helpers write the target offset to `B43legacy_PHY_ILT_G_CTRL`, then write low and optionally high data words to `B43legacy_PHY_ILT_G_DATA1` and `B43legacy_PHY_ILT_G_DATA2`; reads set the control offset and read data word 1. Higher-level PHY code is responsible for iterating tables and choosing offsets.

## State and Persistence
The arrays are immutable kernel data. The helpers mutate hardware PHY ILT registers, which persist in device state until reset or overwritten. No kernel-side dynamic state is owned here.

## Dependencies and Integration Points
Depends on `b43legacy.h`, `ilt.h`, and `phy.h` for register constants and PHY read/write helpers. It integrates with G/B PHY initialization, noise calculations, LO calibration, and interference mitigation in the broader b43legacy PHY subsystem.

## Risks
Table values are hardware magic constants; accidental edits may degrade RF behavior without compile-time errors. `b43legacy_ilt_write32` writes high word before low word, matching expected register semantics. Callers must serialize PHY access according to the driver locking policy.

## Test Signals
Hardware initialization that reaches `b43legacy_phy_init`, stable RSSI/noise readings, successful calibration, and no PHY TX error storm after init are practical signals. Table-size macros should match array initializers at compile time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/ilt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/ilt.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/ilt.h

## Purpose
Declares b43legacy initial lookup-table sizes, exported table symbols, and ILT register access helpers. It is the public interface between PHY calibration code and the table data in `ilt.c`.

## Important APIs, Types, and Functions
Size macros include `B43legacy_ILT_ROTOR_SIZE`, `B43legacy_ILT_RETARD_SIZE`, `B43legacy_ILT_FINEFREQA_SIZE`, `B43legacy_ILT_FINEFREQG_SIZE`, `B43legacy_ILT_NOISEA2_SIZE`, `B43legacy_ILT_NOISEA3_SIZE`, `B43legacy_ILT_NOISEG1_SIZE`, `B43legacy_ILT_NOISEG2_SIZE`, `B43legacy_ILT_NOISESCALEG_SIZE`, and `B43legacy_ILT_SIGMASQR_SIZE`. It declares all matching `extern const` arrays and the helpers `b43legacy_ilt_write`, `b43legacy_ilt_write32`, and `b43legacy_ilt_read`.

## Control Flow
No runtime control flow exists in the header. Consumers use size macros to bound table iteration and helper prototypes to access hardware ILT registers.

## State and Persistence
The header declares immutable table state and hardware-mutating helper APIs. The actual persistent state is in the device PHY ILT registers after writes performed by callers.

## Dependencies and Integration Points
Requires `struct b43legacy_wldev` from included driver headers through consumers. It integrates with `ilt.c` and PHY/radio code that loads calibration constants into the hardware.

## Risks
Size macro drift from actual arrays can cause truncated initialization or out-of-bounds iteration. Because the arrays represent hardware calibration constants, consumers should not reinterpret units or signedness without checking PHY code expectations.

## Test Signals
Compile-time references from PHY code, successful table iteration during PHY init, and stable device calibration after cold start are the main checks. Build warnings for missing symbols catch mismatches with `ilt.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/ilt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/leds.c

## Purpose
Implements optional LED class integration for b43legacy. It maps SPROM GPIO LED behavior values to Linux LED class devices and mac80211 LED triggers for TX, RX, association, and radio state.

## Important APIs, Types, and Functions
Public functions are `b43legacy_leds_init` and `b43legacy_leds_exit`. Internal helpers are `b43legacy_led_turn_on`, `b43legacy_led_turn_off`, `b43legacy_led_brightness_set`, `b43legacy_register_led`, `b43legacy_unregister_led`, and `b43legacy_map_led`.

## Control Flow
Initialization reads four GPIO behavior bytes from SPROM. If an entry is `0xFF`, board-specific defaults are supplied for common Compaq and Asus cases. Each behavior is mapped to direct GPIO on/off or to one or more LED class devices with mac80211 default triggers. Brightness callbacks check software radio and hardware RF switch state, then update the GPIO control bit with active-low handling under `wl->leds_lock`. Exit unregisters all registered LEDs and turns them off.

## State and Persistence
Runtime state lives in `dev->led_tx`, `dev->led_rx`, `dev->led_assoc`, and `dev->led_radio`, each holding LED classdev registration data, GPIO index, active-low flag, device pointer, and name. Hardware GPIO output state persists until changed, reset, or cleanup.

## Dependencies and Integration Points
Depends on LED class, mac80211 LED trigger names, SSB SPROM GPIO fields, PCI vendor IDs for fallback mappings, RF-kill helper `b43legacy_is_hw_radio_enabled`, and b43legacy MMIO GPIO accessors.

## Risks
The brightness callback intentionally accepts a small race reading radio state to avoid heavy locking. Multiple behaviors can map one GPIO to both TX and RX LED devices, so registration failures or duplicate state must be handled gracefully. Incorrect SPROM defaults can invert or mislabel LEDs.

## Test Signals
With `CONFIG_B43LEGACY_LEDS`, validate `/sys/class/leds` entries, TX/RX trigger blinking, association/radio triggers, active-low boards, RF-kill radio LED synchronization, and cleanup on module unload. Disabled LED builds should compile via stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/leds.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/leds.h

## Purpose
Declares b43legacy LED support data structures, SPROM behavior constants, behavior enum, lifecycle APIs, and disabled-build stubs.

## Important APIs, Types, and Functions
When LED support is enabled, `struct b43legacy_led` contains a device pointer, `struct led_classdev`, GPIO index, active-low flag, and name buffer. `B43legacy_LED_BEHAVIOUR` and `B43legacy_LED_ACTIVELOW` decode SPROM values. `enum b43legacy_led_behaviour` covers off/on/activity/radio/mode/transfer/weird/assoc/inactive behaviors. The public APIs are `b43legacy_leds_init` and `b43legacy_leds_exit`.

## Control Flow
Enabled builds expose real initialization and teardown implemented in `leds.c`. Disabled builds define an empty `struct b43legacy_led` and inline no-op lifecycle functions, allowing `struct b43legacy_wldev` to include LED fields unconditionally.

## State and Persistence
Enabled state is per-device LED class registration state and GPIO metadata. Disabled builds carry no LED state. Hardware GPIO persistence is controlled by the implementation, not the header.

## Dependencies and Integration Points
Depends on Linux LED class APIs when `CONFIG_B43LEGACY_LEDS` is set. It integrates with `b43legacy.h` device state and `main.c` core init/exit lifecycle, where LEDs are initialized after core init and removed during core exit.

## Risks
The name length constant must fit generated names using wiphy names. Behavior enum values reflect hardware/SPROM encodings, so reordering is not safe. Disabled stubs must stay source-compatible with enabled APIs.

## Test Signals
Build LED-enabled and disabled configurations, verify generated LED names fit, and inspect sysfs trigger registration on hardware with SPROM LED descriptors and fallback `0xFF` descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/leds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/main.c

## Purpose
Implements the b43legacy driver core: module parameters, SSB probe/remove, mac80211 registration and operations, firmware loading/upload, chip/core init and teardown, interrupt handling, beacon/template management, TX workqueue, periodic calibration/noise work, RF/radio configuration, suspend/resume, restart recovery, and low-level SHM/TSF/MMIO helpers.

## Important APIs, Types, and Functions
Key lifecycle functions are `b43legacy_probe`, `b43legacy_remove`, `b43legacy_wireless_init`, `b43legacy_one_core_attach`, `b43legacy_wireless_core_attach`, `b43legacy_wireless_core_init`, `b43legacy_wireless_core_start`, `b43legacy_wireless_core_stop`, `b43legacy_wireless_core_exit`, and `b43legacy_controller_restart`. mac80211 ops include TX, config, BSS changes, filter configuration, add/remove interface, start/stop, TIM update, survey, stats, and rfkill poll. Hardware helpers include SHM read/write, TSF read/write, MAC suspend/enable, GPIO init/cleanup, chip init, firmware upload/initvals, IRQ top/bottom halves, beacon/probe template writers, and retry/rate memory setup.

## Control Flow
Module init creates debugfs and registers an SSB driver. Probe allocates a mac80211 hw object on the first core, attaches each SSB core, performs lightweight PHY/radio discovery, adds debugfs, and schedules firmware loading. Firmware work requests ucode/PCM/initval files and registers the hw with mac80211. `start` initializes the core if needed, uploads firmware and initvals, initializes PHY/radio/GPIO/DMA or PIO/security/RNG/LEDs, requests IRQ, enables MAC/queues/interrupts, and schedules periodic work. TX from mac80211 is queued per priority and drained by workqueue into DMA or PIO. IRQ top half snapshots reason registers, acknowledges/masks interrupts, and schedules a tasklet; the tasklet processes DMA RX, TX status, beacon slots, TBTT/ATIM/PMQ, noise samples, DMA errors, and restart triggers. Stop disables IRQs, synchronizes tasklet, cancels work, drains queues, suspends MAC, and frees IRQ; exit stops firmware PSM, frees transfer backends and calibration memory, disables radio/analog/core, and powers down the bus.

## State and Persistence
Live state spans `b43legacy_wl` and `b43legacy_wldev`: current core, interface mode, BSSID/MAC, filter flags, queues, beacon skb/template flags, firmware refs, PHY calibration data, IRQ masks/reasons, DMA/PIO backend state, key table pointer, radio flags, RNG/LED/debugfs state, and initialization status. Hardware state persists in SHM, template RAM, GPIO, MMIO control registers, TSF registers, firmware PSM memory, and radio/PHY registers until reset or powerdown.

## Dependencies and Integration Points
Integrates with SSB, mac80211, firmware loader, Linux workqueues/tasklets/IRQs, DMA/PIO modules, PHY/radio/sysfs/rfkill/xmit/debugfs/LED modules, hwrng, PCI/SPROM board data, and kernel PM. Firmware files under `b43legacy*/` are external runtime dependencies.

## Risks
This file has high concurrency risk: `wl->mutex`, `irq_lock`, tasklet, workqueues, and IRQ masking must stay ordered. Firmware and initval format validation is strict but firmware availability fails at runtime. Restart, suspend/resume, and remove paths must coordinate queued work and firmware completion. Beacon template updates are asynchronous to avoid firmware transmitting partially updated templates. Some code is explicitly FIXME/TODO, including limited queue mapping, probe response handling, AP power-save, and ucode debug.

## Test Signals
Critical signals include probe/register/unregister with firmware present and absent, start/stop cycles, DMA and PIO traffic, association as STA, AP/IBSS beacon template updates, channel and retry-limit reconfiguration, RF-kill and software radio toggles, suspend/resume, controller restart after injected DMA/PHY errors, debugfs restart, hwrng registration, and lockdep under traffic plus module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/main.h

## Purpose
Declares shared helpers implemented by `main.c` and small inline utilities for b43legacy channel/rate conversion. It also defines the padding macro used by packed firmware-facing structures.

## Important APIs, Types, and Functions
Defines `PAD_BYTES` through token-pasting helper macros. Inline helpers are `b43legacy_freq_to_channel_bg`, `b43legacy_freq_to_channel`, `b43legacy_channel_to_freq_bg`, `b43legacy_channel_to_freq`, `b43legacy_is_cck_rate`, and `b43legacy_is_ofdm_rate`. Prototypes cover TSF access, SHM access, host-flag read/write, dummy transmission, wireless core reset, MAC suspend/enable, and controller restart.

## Control Flow
Inline channel conversion maps 2.4 GHz frequencies to channel IDs, with channel 14 handled specially at 2484 MHz. Rate helpers classify the four CCK hardware rates and treat all other b43legacy rates as OFDM. The declared functions are called by PHY/radio/xmit/debugfs/DMA paths to manipulate shared memory, timing, and MAC/core state.

## State and Persistence
The header itself owns no state. Its APIs mutate persistent hardware state: SHM contents, host flags, TSF registers, template RAM indirectly through dummy transmission/core reset, MAC enabled/suspended state, and restart work scheduling.

## Dependencies and Integration Points
Includes `b43legacy.h` for device types and rate constants. It is a cross-module interface between `main.c`, xmit, debugfs, DMA/PIO, PHY, and radio code.

## Risks
Rate classification depends on constants where rate values equal Mbps times two; changing constants breaks PLCP and rate-table logic. Channel helpers only support 2.4 GHz BG behavior, which matches b43legacy scope but would be wrong for 5 GHz. Padding macros affect packed firmware structures and should not be casually changed.

## Test Signals
Compile all users, verify channel 1/6/11/14 conversions, validate CCK/OFDM PLCP generation through TX tests, and confirm SHM/TSF/debugfs accessors link correctly. Core reset and MAC suspend/enable behavior are validated through start/stop and suspend/resume cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/main.h -->
