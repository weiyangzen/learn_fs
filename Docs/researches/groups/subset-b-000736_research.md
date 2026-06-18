# Research: subset-b-000736

Grouped research for OCTEON MIPS CVMX hardware headers and adjacent MIPS architecture hooks in the Ceph client source tree.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pow.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pow.h

Purpose: exposes the OCTEON Packet Order / Work (POW) unit programming interface. It defines tag states, tag operations, POW load/store address encodings, load-response formats, and inline helpers for requesting work, switching tags, submitting work queue entries, descheduling work, and configuring per-core group and priority masks.

Important APIs/types/functions: `enum cvmx_pow_tag_type` models ordered, atomic, null, and null-null tag states. `cvmx_pow_wait_t` selects blocking versus nonblocking work requests. `cvmx_pow_tag_op_t` enumerates store operations such as `SWTAG`, `SWTAG_FULL`, `SWTAG_DESCH`, `DESCH`, `ADDWQ`, `UPDATE_WQP_GRP`, and no-schedule controls. Key unions include `cvmx_pow_tag_req_t`, `cvmx_pow_load_addr_t`, `cvmx_pow_tag_load_resp_t`, `cvmx_pow_tag_store_addr_t`, and `cvmx_pow_iobdma_store_t`. The main inline functions are `cvmx_pow_get_current_tag`, `cvmx_pow_get_current_wqp`, `cvmx_pow_tag_sw_wait`, sync/async work request and response helpers, `cvmx_pow_tag_sw*`, `cvmx_pow_tag_sw_full*`, `cvmx_pow_tag_sw_null*`, `cvmx_pow_work_submit`, `cvmx_pow_set_group_mask`, `cvmx_pow_set_priority`, `cvmx_pow_tag_sw_desched*`, `cvmx_pow_desched`, and tag bit compose/extract helpers. External diagnostics are `cvmx_pow_capture`, `cvmx_pow_display`, and `cvmx_pow_get_num_entries`.

Control flow: work-request helpers build an I/O-space POW load address with the correct DID and wait bit, issue `cvmx_read_csr` or `cvmx_send_single`, then decode the returned WQE physical address or no-work bit. Tag switch helpers first optionally warn about pending switches, wait for the CHORD hardware completion bit when using checked wrappers, populate `cvmx_pow_tag_req_t`, and store the request to the POW DID that sets, preserves, or clears the local pending-switch bit. `cvmx_pow_work_submit` writes tag/qos/group fields into the WQE, issues `CVMX_SYNCWS`, then submits the WQE physical address to POW. Deschedule helpers synchronize WQE writes and use TAG3 stores so the pending-switch bit is cleared immediately.

State and persistence: no persistent software state is owned by this header. It manipulates live POW hardware state: current core tag, WQE pointer, POW entry lists, group masks, static priorities, deschedule/noschedule bits, and scratch-memory async responses. Caller-visible state is in WQE memory and processor-local scratch space; diagnostics can capture hardware state into caller-provided buffers.

Dependencies and integration points: includes `cvmx-pow-defs.h`, `cvmx-scratch.h`, and `cvmx-wqe.h`; relies on `cvmx.h` CSR/IO helpers, `cvmx_get_core_num`, `cvmx_get_cycle`, `cvmx_phys_to_ptr`, `cvmx_ptr_to_phys`, `cvmx_build_mask`, OCTEON DID constants, `CVMX_SYNCWS`, `CVMX_SYNCIOBDMA`, and kernel logging. It is the bridge between packet receive/submit code and the POW scheduler used by OCTEON network datapaths.

Risks: ordering is hardware-sensitive; using no-check functions with a pending tag switch can deadlock or corrupt scheduling state. Switching to NULL via the normal switch path is explicitly unsafe because completion will never clear. Descheduling to ORDERED has hardware caveats and the header recommends ATOMIC for the rescheduled state. Async APIs require 8-byte-aligned scratch addresses and an explicit `CVMX_SYNCIOBDMA` before reading responses. `CVMX_ENABLE_POW_CHECKS` emits warnings but does not prevent invalid operations. Several bitfield comments note duplicate or typo-like fields, so maintainers must preserve hardware layout rather than "cleaning up" names casually.

Test signals: meaningful validation requires OCTEON hardware or an architectural simulator. Compile-time coverage should include both endian bitfield layouts and users of sync/async POW helpers. Runtime signals include absence of pending-switch warnings, no long waits in `cvmx_pow_tag_sw_wait`, correct WQE physical pointer conversion, POW group/priorities matching scheduler expectations, and packet throughput tests that exercise ordered and atomic tag paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-rnm-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-rnm-defs.h

Purpose: describes the OCTEON Random Number Module (RNM) CSR address map and register bitfields for entropy collection, random-number enable/reset control, extended entropy register access, BIST status, and serial number access.

Important APIs/types/functions: address macros include `CVMX_RNM_CTL_STATUS`, `CVMX_RNM_BIST_STATUS`, `CVMX_RNM_EER_KEY`, `CVMX_RNM_EER_DBG`, and `CVMX_RNM_SERIAL_NUM`. Unions include `cvmx_rnm_bist_status`, `cvmx_rnm_ctl_status`, `cvmx_rnm_eer_dbg`, `cvmx_rnm_eer_key`, and `cvmx_rnm_serial_num`. `cvmx_rnm_ctl_status` has generic plus CN30XX, CN50XX, and CN63XX views for feature-specific fields such as entropy enable, RNG enable, resets, entropy-source select, extended entropy validity/lock, and mask-disable behavior.

Control flow: this header has no executable control flow. Drivers read or write the generated CSR addresses through `cvmx_read_csr`/`cvmx_write_csr`, select the chip-specific union view, and interpret or set bitfields.

State and persistence: state is entirely in hardware CSRs. Reset and enable bits affect live RNM/RNG operation. Serial number and EER registers expose hardware-provided values; no software cache is maintained.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` from `cvmx.h` and the kernel/OCTEON bitfield convention. It is included by `octeon-feature.h`, where fuse/feature checks use RNM-related definitions, and by random or crypto-capability initialization code.

Risks: writing reset and enable fields in the wrong sequence can disable entropy generation. Chip-specific struct views differ, so using the generic view on older models can read or write reserved bits. The header does not enforce locking around EER access despite fields such as `eer_lck`.

Test signals: build tests should verify the header compiles for big- and little-endian bitfields. Runtime hardware tests should check BIST pass bits, RNG enable/reset transitions, EER valid/lock behavior, and feature-probe paths that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-rnm-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-rst-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-rst-defs.h

Purpose: defines OCTEON reset, boot, power, PCIe reset, and BIST-clear CSR addresses and packed register layouts.

Important APIs/types/functions: macros cover `CVMX_RST_BOOT`, `CVMX_RST_CFG`, `CVMX_RST_CKILL`, indexed `CVMX_RST_CTLX`, `CVMX_RST_DELAY`, `CVMX_RST_ECO`, `CVMX_RST_INT`, `CVMX_RST_OCX`, `CVMX_RST_POWER_DBG`, `CVMX_RST_PP_POWER`, indexed `CVMX_RST_SOFT_PRSTX`, and `CVMX_RST_SOFT_RST`. Unions include `cvmx_rst_boot`, `cvmx_rst_cfg`, `cvmx_rst_ckill`, `cvmx_rst_ctlx`, `cvmx_rst_delay`, `cvmx_rst_eco`, `cvmx_rst_int`, `cvmx_rst_ocx`, `cvmx_rst_power_dbg`, `cvmx_rst_pp_power`, `cvmx_rst_soft_prstx`, and `cvmx_rst_soft_rst`.

Control flow: the file is declarative. Platform reset code reads boot straps and PLL multipliers, writes BIST-clear policy and reset delays, controls per-link reset bits through `RST_CTLX`/`SOFT_PRSTX`, and can trigger a chip-wide software reset via `soft_rst`.

State and persistence: all state is hardware reset-domain state. Some fields reflect boot-time straps (`lboot`, `rboot`, multipliers, JTAG/EJTAG disable flags), while others control active reset and power-gating state. A software reset or processor power gate has system-wide effects and persists only until the next reset cycle reinitializes hardware.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` and the OCTEON CSR access layer. It integrates with board boot, PCIe root-complex/endpoint setup, CPU power management, and reset interrupt handling.

Risks: mistaken writes can reset links, processors, or the full chip. Indexed macros mask offsets with `& 3`; out-of-range callers silently alias to one of four registers. CN70XX variants narrow some fields, so generic code can misinterpret gate or interrupt bit widths. BIST-clear fields must be coordinated with diagnostics to avoid losing failure evidence.

Test signals: hardware validation should verify boot strap decoding, reset interrupt bits, PCIe link reset sequencing, and soft-reset paths. Static tests should compile both endian layouts and chip-specific union views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-rst-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-scratch.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-scratch.h

Purpose: provides typed volatile accessors for OCTEON processor-local scratchpad memory.

Important APIs/types/functions: `CVMX_SCRATCH_BASE` is the negative address base for local scratch memory. Read helpers are `cvmx_scratch_read8`, `cvmx_scratch_read16`, `cvmx_scratch_read32`, and `cvmx_scratch_read64`. Write helpers are `cvmx_scratch_write8`, `cvmx_scratch_write16`, `cvmx_scratch_write32`, and `cvmx_scratch_write64`.

Control flow: each inline helper computes `CVMX_SCRATCH_BASE + address`, casts it to the corresponding volatile integer pointer with `CASTPTR`, and performs one load or store. There is no bounds checking, locking, or synchronization in the helpers.

State and persistence: scratchpad contents are per-processor, volatile runtime state. They are used for low-latency temporary storage and IOBDMA response slots; they do not persist across reset or core context assumptions.

Dependencies and integration points: depends on `CASTPTR` from `cvmx.h`. `cvmx-pow.h` uses scratch reads for asynchronous POW work responses, and other CVMX code can use scratch offsets for IOBDMA and per-core temporary values.

Risks: callers must supply valid byte offsets and natural alignment for the access width. Comments for `cvmx_scratch_write16` and `cvmx_scratch_write32` describe the wrong width, which can mislead maintainers even though the implementations are correctly typed. Scratch storage is local to a processor, so sharing assumptions across cores are invalid.

Test signals: tests are primarily compile-time and hardware/runtime checks. Useful signals include successful async IOBDMA/POW responses in scratch, no alignment exceptions, and no cross-core data-sharing assumptions in call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-scratch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sli-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sli-defs.h

Purpose: defines selected OCTEON SLI/PCIe interface registers used for MSI receive addressing, port interrupt mapping, memory access timing, S2M port control, and memory-access subindex setup.

Important APIs/types/functions: `CVMX_SLI_PCIE_MSI_RCV` expands to `CVMX_SLI_PCIE_MSI_RCV_FUNC`, which returns a model-dependent MSI receive offset. Unions are `cvmx_sli_ctl_portx`, `cvmx_sli_mem_access_ctl`, `cvmx_sli_s2m_portx_ctl`, and `cvmx_sli_mem_access_subidx`, the last with a CN68XX layout variant.

Control flow: the one inline function switches on `cvmx_get_octeon_family()` and uses `OCTEON_IS_MODEL(OCTEON_CN78XX_PASS1_X)` to select the legacy versus newer MSI receive offset. All other content is passive CSR layout data for callers to read and write.

State and persistence: state is live PCIe/SLI hardware configuration. Port disable, interrupt routing, memory access timers, maximum word settings, read/write type, endian-swap controls, and base-address fields persist in CSRs until reset or reconfiguration.

Dependencies and integration points: includes `<uapi/asm/bitfield.h>` and relies on OCTEON model macros from `octeon-model.h`. It integrates with PCIe host/endpoint setup, MSI handling, SLI DMA windows, and memory-mapped access policy.

Risks: MSI address selection is chip-family sensitive; using the wrong offset can break interrupt delivery. CN68XX uses a different base-address field width, so generic programming can write invalid low bits. Port and endian-swap controls are low-level and can make PCIe memory windows inaccessible if misconfigured.

Test signals: runtime PCIe enumeration and MSI delivery are the main tests. Model-matrix tests should verify the returned MSI receive offset for CN6XXX, CN70XX, CN78XX pass 1, and newer CN7XXX families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sli-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spi.h

Purpose: declares the OCTEON SPI4 packet-interface initialization API and callback hooks.

Important APIs/types/functions: `cvmx_spi_mode_t` defines unknown, TX halfplex, RX halfplex, and duplex modes. `cvmx_spi_callbacks_t` contains reset, calendar setup, clock detection, training, calendar synchronization, and interface-up callbacks. Inline helpers are `cvmx_spi_is_spi_interface`, `cvmx_spi4000_is_present`, `cvmx_spi4000_initialize`, and `cvmx_spi4000_check_speed`. External functions include `cvmx_spi_start_interface`, `cvmx_spi_restart_interface`, callback get/set APIs, and default callback implementations.

Control flow: callers detect SPI mode by reading `CVMX_GMXX_INF_MODE(interface)` and checking mode bits. Interface start/restart is implemented elsewhere through the callback sequence: reset DLL, configure calendar, detect clocks, train link, synchronize calendars, then mark interface up. SPI4000 helpers are stubs returning no device or zeroed status.

State and persistence: callback configuration is external state managed by the implementation file. Hardware state lives in GMX/SPI CSRs and link-training state. The header itself holds no state.

Dependencies and integration points: includes `cvmx-gmxx-defs.h` and uses `cvmx_read_csr`. It integrates with SPI4 network-interface bring-up, board-specific callback overrides, and GMX in-band status structures.

Risks: the SPI4000 functions are stubbed, so code that expects real SPI4000 support will silently see no device. Callback failures abort initialization, and timeout units differ between clock detection/training/calendar synchronization comments. The typo "corespondant" is harmless but indicates older SDK text.

Test signals: hardware tests should cover SPI interface detection, start/restart callback ordering, timeout behavior, and link-up state. Unit coverage can mock callbacks to verify abort and sequencing logic in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spinlock.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spinlock.h

Purpose: implements CVMX spinlocks for synchronization with the OCTEON boot monitor and non-Linux programs, distinct from Linux kernel spinlocks.

Important APIs/types/functions: `cvmx_spinlock_t` wraps a volatile 32-bit value. Constants define unlocked/locked values and an initializer. APIs are `cvmx_spinlock_init`, `cvmx_spinlock_locked`, `cvmx_spinlock_unlock`, `cvmx_spinlock_trylock`, `cvmx_spinlock_lock`, plus bit-lock variants `cvmx_spinlock_bit_lock`, `cvmx_spinlock_bit_trylock`, and `cvmx_spinlock_bit_unlock`.

Control flow: lock and trylock use MIPS `ll`/`sc` loops in inline assembly. Full-word locks spin until the value is zero and then store one. Bit locks test and set bit 31 while preserving the lower 31 bits. Unlock paths issue `CVMX_SYNCWS`, clear the lock word or bit, and issue another `CVMX_SYNCWS`.

State and persistence: lock state is in caller-provided memory. It is volatile process/hardware synchronization state only. The bit-lock form intentionally shares a word with low 31 data bits protected by the lock.

Dependencies and integration points: includes `cvmx-asm.h` for synchronization and OCTEON/MIPS assembly helpers. Intended integration is firmware/monitor/shared-memory coordination, not Linux `spinlock_t` replacement.

Risks: these locks lack Linux lockdep, IRQ, preemption, and SMP debug semantics. Bit unlock is non-atomic and assumes the lower bits are protected by the lock. Inline assembly uses `$at` and OCTEON bit instructions, so toolchain/ISA compatibility matters. Recursive lock debugging is disabled by default.

Test signals: compile tests must target the OCTEON MIPS assembler. Runtime tests should exercise lock acquisition under contention, trylock return semantics matching Linux convention, memory ordering around shared monitor data, and bit-lock preservation of lower bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spxx-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spxx-defs.h

Purpose: describes common SPI4/SPX interface CSRs for clocks, deskew, driver strength, error handling, interrupt masks/status, training pattern accounting, and BIST.

Important APIs/types/functions: address macros cover `CVMX_SPXX_BCKPRS_CNT`, `BIST_STAT`, `CLK_CTL`, `CLK_STAT`, `DBG_DESKEW_CTL`, `DBG_DESKEW_STATE`, `DRV_CTL`, `ERR_CTL`, `INT_DAT`, `INT_MSK`, `INT_REG`, `INT_SYNC`, `TPA_ACC`, `TPA_MAX`, `TPA_SEL`, and `TRN4_CTL`, indexed by `block_id`. `__cvmx_interrupt_spxx_int_msk_enable` is declared for interrupt unmasking. Register unions provide fields for backpressure counts, BIST status, DLL/clock training controls, deskew state, CN38XX/CN58XX drive controls, error counters, interrupt causes/masks, TPA counters, and training controls.

Control flow: no logic is implemented beyond address calculation. Drivers program clock/training registers, poll status, enable interrupt masks, and clear or inspect interrupt/status registers via CSR accessors.

State and persistence: all state is SPX hardware state. Counters accumulate until reset/clear by hardware policy. Interrupt masks and training controls persist in CSRs until changed or reset.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` and OCTEON endian bitfield conventions. It is used by SPI4 initialization and interrupt code alongside `cvmx-srxx-defs.h`, `cvmx-stxx-defs.h`, and `cvmx-spi.h`.

Risks: `block_id` is masked with `& 1`, so invalid IDs alias silently. Clock/training/deskew fields are timing-sensitive; incorrect writes can prevent link synchronization. CN38XX and CN58XX drive-control layouts differ. Interrupt register, mask, and sync registers carry similar field names but different semantics, so write-one-to-clear versus mask behavior must be checked in callers.

Test signals: hardware bring-up should check BIST, stable clock status bits, successful training, expected interrupt causes under injected SPI errors, and backpressure/TPA counters during traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spxx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sriox-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sriox-defs.h

Purpose: provides the large OCTEON SRIO controller CSR map and bitfield definitions for access control, assembly ID, BIST, inbound/outbound messages, doorbells, interrupts, maintenance operations, memory operations, S2M mappings, tag control, credits, link status, and transmit/receive status.

Important APIs/types/functions: address macros include `CVMX_SRIOX_ACC_CTRL`, `ASMBLY_ID`, `ASMBLY_INFO`, `BELL_RESP_CTRL`, `BIST_STATUS`, `IMSG_*`, `INT_ENABLE`, `INT_REG`, `INT_INFO0-3`, `IP_FEATURE`, `MAC_BUFFERS`, `MAINT_OP`, `MAINT_RD_DATA`, `MEM_OP_CTRL`, `OMSG_*`, `PRIOX_IN_USE`, `RX_BELL`, `RX_STATUS`, `S2M_TYPEX`, `STATUS_REG`, `TAG_CTRL`, `TLP_CREDITS`, `TX_BELL`, `TX_CTRL`, `TX_STATUS`, and write-done counters. Register unions mirror those groups and include chip-specific CN63XX/CN63XX pass-1 variants where fields differ.

Control flow: the header is declarative. SRIO code uses these macros to configure link access, enable/inspect interrupts, initiate maintenance reads/writes through `MAINT_OP` and `MAINT_RD_DATA`, set inbound message QoS/group mapping, configure outbound message matching/ports, process doorbells, and monitor credits/status.

State and persistence: all state is SRIO hardware state in CSRs, including link status, error/interrupt latches, doorbell FIFOs, message queues, credit counters, retry thresholds, and access-control denial bits. No software persistence is held here.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` and bitfield endian configuration. It integrates with OCTEON SRIO drivers and with feature probes that gate SRIO support to relevant models.

Risks: this file contains hardware errata-like layout variants and apparent duplicated field names in some generated structs, so compiler behavior and field selection must be treated carefully. Indexed macros mask block IDs, queue offsets, and priority offsets, which silently aliases invalid inputs. Interrupt enable/status fields are dense and easy to mismatch. Maintenance operations expose pending/fail bits; callers must poll correctly before using read data. SRIO access-deny bits can block BAR or address windows.

Test signals: hardware tests should cover SRIO link up/down interrupts, doorbell send/receive, maintenance read/write completion and fail paths, inbound/outbound message queues, credit counters, and CN63XX pass-1 layout handling. Compile tests should cover both endian bitfield modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sriox-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-srxx-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-srxx-defs.h

Purpose: defines SPI4 receive-side SRX CSR addresses and register layouts.

Important APIs/types/functions: macros include `CVMX_SRXX_COM_CTL`, `CVMX_SRXX_IGN_RX_FULL`, indexed `CVMX_SRXX_SPI4_CALX`, `CVMX_SRXX_SPI4_STAT`, `CVMX_SRXX_SW_TICK_CTL`, and `CVMX_SRXX_SW_TICK_DAT`. Unions include `cvmx_srxx_com_ctl`, `cvmx_srxx_ign_rx_full`, `cvmx_srxx_spi4_calx`, `cvmx_srxx_spi4_stat`, `cvmx_srxx_sw_tick_ctl`, and `cvmx_srxx_sw_tick_dat`.

Control flow: receive initialization code programs calendar entries, enables the interface and status tracking, configures ignored full conditions, reads calendar/status fields, and can inject software tick control/data values. No functions execute in this header.

State and persistence: state lives in SRX hardware CSRs. Calendar entries and interface-enable bits persist until reset/reconfiguration; status and tick data reflect live receive hardware.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG`. It pairs with `cvmx-stxx-defs.h` for transmit-side SPI4 and `cvmx-spxx-defs.h` for common SPX control during `cvmx-spi` initialization.

Risks: `block_id` and calendar offsets are masked, so invalid values alias. Calendar parity and port fields must match the peer SPI4 calendar or receive synchronization fails. There are no helper functions enforcing proper enable/order sequencing.

Test signals: SPI4 receive link tests should verify calendar programming, `inf_en`/`st_en` behavior, receive-full handling, status length/m fields, and software tick diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-srxx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-stxx-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-stxx-defs.h

Purpose: defines SPI4 transmit-side STX CSR addresses and register layouts for arbitration, calendars, interrupts, statistics, backpressure, and transmit control.

Important APIs/types/functions: macros include `CVMX_STXX_ARB_CTL`, `BCKPRS_CNT`, `COM_CTL`, `DIP_CNT`, `IGN_CAL`, `INT_MSK`, `INT_REG`, `INT_SYNC`, `MIN_BST`, indexed `SPI4_CALX`, `SPI4_DAT`, `SPI4_STAT`, `STAT_BYTES_HI/LO`, `STAT_CTL`, and `STAT_PKT_XMT`. `__cvmx_interrupt_stxx_int_msk_enable` is declared. Unions describe arbitration controls, counters, enable controls, DIP/frame error limits, calendar ignore masks, interrupt masks/status/sync, minimum burst, SPI4 calendar/data/status, and statistics.

Control flow: no executable logic is present. SPI4 transmit setup writes calendar and timing registers, enables the interface, configures interrupt masks, and reads/clears statistics and error causes.

State and persistence: all state is hardware CSR state. Packet/byte/backpressure counters are live hardware counters; interrupt status reflects latched transmit faults; calendar/control registers persist until reset.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` and endian bitfields. It integrates with `cvmx-spi.h` initialization, the common SPX block, and SRX receive-side definitions.

Risks: `block_id` and calendar offsets are masked and can alias invalid inputs. Transmit calendar parity, DIP settings, minimum burst, and ignored calendar fields must match the external SPI4 peer. Interrupt mask/status/sync field overlap can cause accidental missed or uncleared faults if caller semantics are wrong.

Test signals: hardware tests should verify transmit calendar setup, interface enable, packet/byte counters under traffic, error interrupt injection, and backpressure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-stxx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sysinfo.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sysinfo.h

Purpose: defines the CVMX system-information structure populated from the OCTEON bootloader descriptor and declares the accessor for that information.

Important APIs/types/functions: `struct cvmx_sysinfo` contains installed DRAM size, bootmem descriptor physical address, stack/heap locations and sizes, running core mask, deprecated init core, exception base, CPU clock, DRAM data rate, board type/revision, MAC base/count, board serial number, compact-flash physical base addresses, LED display base, DFA reference clock, bootloader config flags, and console UART. `cvmx_sysinfo_get()` returns the global structure pointer.

Control flow: the header has no inline logic. Initialization code elsewhere populates the structure from bootloader data or via minimal initialization for Linux/u-boot/simple executive consumers; callers retrieve it with `cvmx_sysinfo_get`.

State and persistence: the structure is process/kernel memory state reflecting bootloader-provided platform facts. It persists for the boot lifetime and is read by timing, board, memory, and device code. It is not durable beyond boot.

Dependencies and integration points: includes `cvmx-coremask.h`. `cvmx.h` uses `cvmx_sysinfo_get()->cpu_clock_hz` in timeout calculations, and board/device code uses MAC, board, compact flash, LED, and console fields.

Risks: many CVMX helpers assume `cpu_clock_hz` and other required fields are initialized. `init_core` is deprecated and can be wrong for complex core masks. Physical addresses in optional board fields require correct address-space conversion by callers.

Test signals: boot tests should verify sysinfo population from descriptors, sane clock rates, valid core mask, MAC count/base, and correct timeout behavior in `CVMX_WAIT_FOR_FIELD64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sysinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-uctlx-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-uctlx-defs.h

Purpose: describes OCTEON USB controller (UCTL) CSRs for clock/reset, PHY control, EHCI/OHCI behavior, interrupt status/enable, timeout controls, BIST, watermarks, and interface enable.

Important APIs/types/functions: address macros include `CVMX_UCTLX_CLK_RST_CTL`, `UPHY_CTL_STATUS`, indexed `UPHY_PORTX_CTL_STATUS`, `INT_REG`, `INT_ENA`, `IF_ENA`, `PPAF_WM`, `EHCI_CTL`, `OHCI_CTL`, `ERTO_CTL`, `ORTO_CTL`, `BIST_STATUS`, and `EHCI_FLA`. Unions define fields for BIST blocks, clock divisors/resets, PHY reset/power/refclk, EHCI/OHCI L2 cache and address controls, timeout values, interrupt bits, watermark, PHY BIST/status, and port tuning/test controls.

Control flow: the header is declarative. USB platform code sequences resets/clocks, programs PHY tuning and host-controller controls, enables the interface, configures interrupts, and polls BIST/PHY status through these layouts.

State and persistence: state is USB controller and PHY CSR state. Clock/reset controls and interface-enable persist until reset or reconfiguration. Interrupt bits and BIST status are live hardware latches.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG`. It integrates with OCTEON USB host initialization, EHCI/OHCI platform drivers, and feature detection for `OCTEON_FEATURE_USB`.

Risks: most macros ignore `block_id`; `UPHY_PORTX_CTL_STATUS` masks the block contribution to zero and only varies by port offset, so assuming multiple blocks would alias. Reset/clock sequencing is fragile and not enforced by types. PHY tuning fields can break signal integrity. Timeout and interrupt fields have similar names for enable and status registers.

Test signals: USB bring-up should verify BIST pass, PHY reset release, EHCI/OHCI register access, interrupt delivery, device enumeration, timeout handling, and port tuning defaults on supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-uctlx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-wqe.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-wqe.h

Purpose: defines the OCTEON work queue entry (WQE) format used by POW, PIP, packet receive, and software-submitted work paths.

Important APIs/types/functions: `OCT_TAG_TYPE_STRING` maps tag types to names. The large decode union at the top captures hardware receive classification and error bits for IP and non-IP packets, including VLAN, port/PKND, checksum/error flags, broadcast/multicast, fragmentation, and buffer count. Other key types are `union cvmx_pip_wqe_word0`, `union cvmx_wqe_word0`, `union cvmx_wqe_word1`, and `struct cvmx_wqe`. Accessors `cvmx_wqe_get_port`, `cvmx_wqe_set_port`, `cvmx_wqe_get_grp`, `cvmx_wqe_set_grp`, `cvmx_wqe_get_qos`, and `cvmx_wqe_set_qos` hide layout differences.

Control flow: packet hardware fills WQE fields, POW schedules the entry, and software reads/updates metadata through direct fields and accessors. Accessors branch on `octeon_has_feature(OCTEON_FEATURE_CN68XX_WQE)` where CN68XX-style WQE layouts differ for port/group/qos placement.

State and persistence: WQE instances are in memory and represent live packet/work metadata. They are not durable, but correctness is critical while POW owns or schedules the entry. Some fields are hardware-written and should not be casually overwritten.

Dependencies and integration points: includes `cvmx-packet.h`; relies on tag-type values from `cvmx-pow.h` and feature detection from `octeon-feature.h`/model headers. `cvmx-pow.h` uses `struct cvmx_wqe` for work requests and submissions. Network receive/transmit and packet classification code consume decode/error fields.

Risks: bitfield layouts are endian- and model-dependent. CN68XX WQE differences require accessors; direct field access can break on those chips. Hardware and software share ownership of fields at different times, so missing `CVMX_SYNCWS` before POW submission can expose stale data. The decode union contains many error conditions that callers must interpret correctly to avoid accepting malformed packets.

Test signals: packet receive tests should verify WQE port/group/qos accessors on CN68XX and non-CN68XX models, VLAN/error decode, buffer count handling, and POW submit/request round trips. Compile coverage should include both endian bitfield modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-wqe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx.h

Purpose: provides the core CVMX utility layer for OCTEON: address-space construction, CSR and I/O access, physical/virtual conversion, processor/core identity, node-aware CSR access, bit helpers, cycle counters, polling macros, and core-count discovery.

Important APIs/types/functions: address macros include `CVMX_ADD_SEG`, `CVMX_ADD_IO_SEG`, and 32-bit variants. Constants include `CVMX_MAX_CORES`, cache line size/alignment, and node masks/shifts. Helpers include `cvmx_get_proc_id`, `cvmx_build_mask`, `cvmx_build_io_address`, `cvmx_build_bits`, `cvmx_ptr_to_phys`, `cvmx_phys_to_ptr`, generated typed `cvmx_read64_*`/`cvmx_write64_*`, `cvmx_write_csr`, `cvmx_writeq_csr`, `cvmx_write_io`, `cvmx_read_csr`, `cvmx_readq_csr`, `cvmx_send_single`, `cvmx_read_csr_async`, `cvmx_octeon_is_pass1`, `cvmx_get_core_num`, node/local-core helpers, `cvmx_write_csr_node`, `cvmx_read_csr_node`, `cvmx_pop`, `cvmx_dpop`, `cvmx_get_cycle`, `cvmx_get_cycle_global`, `CVMX_WAIT_FOR_FIELD64`, and `cvmx_octeon_num_cores`.

Control flow: CSR writes issue a volatile store and, for RSL-space addresses, read `CVMX_MIO_BOOT_BIST_STAT` to force completion. Async CSR reads encode an IOBDMA SENDSINGLE request into scratch memory. Node CSR helpers splice node bits into the address. `CVMX_WAIT_FOR_FIELD64` repeatedly reads a CSR field until a predicate is true or a CPU-clock-derived timeout expires. Core count reads CIU/CIU3 fuse registers and counts set bits.

State and persistence: this header holds no persistent state. It directly reads/writes hardware CSRs, cycles, fuses, and address spaces. Timeout behavior depends on `cvmx_sysinfo_get()->cpu_clock_hz`.

Dependencies and integration points: includes Linux kernel headers, delay support, CVMX assembly/packet/sysinfo headers, many CSR definition headers, bootinfo/bootmem, and L2 cache helpers. It is foundational for nearly every OCTEON-specific header in this group.

Risks: pointer/physical conversions mask addresses differently for 32-bit, 64-bit XKSEG/XKPHYS, and hardware limits; misuse can produce inaccessible or truncated DMA addresses. `cvmx_build_mask(bits)` is unsafe for `bits == 64` in plain C shift terms if called that way. `CVMX_WAIT_FOR_FIELD64` depends on initialized sysinfo clock and can busy wait. CSR completion read is address-space-specific. Node address composition must preserve non-node bits.

Test signals: hardware smoke tests should cover CSR read/write completion, physical pointer round trips for DMA buffers, cycle-counter monotonicity, timeout macro behavior, node CSR access on multi-node systems, and core-count fuse interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon-feature.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon-feature.h

Purpose: centralizes OCTEON feature detection by mapping model families and selected fuse registers to named hardware capabilities.

Important APIs/types/functions: `enum octeon_feature` lists capabilities such as PKND, CN68XX WQE layout, SAAD atomics, ZIP, dormant crypto, PCIe, SRIO, Interlaken, key memory, LED controller, trace buffer, management port, RAID, USB, no-WQE IPD mode, DFA, MDIO clause 45, NPEI, HFA, DFM, CIU2/CIU3, FPA3, and FAU. `enum octeon_feature_bits` includes `OCTEON_HAS_CRYPTO`, backed by external `__octeon_feature_bits`. `octeon_has_crypto()` checks that cached bit. `octeon_has_feature()` is a switch-based inline model/fuse probe.

Control flow: `octeon_has_feature` uses `OCTEON_IS_MODEL` predicates for most capabilities. Dormant crypto additionally reads `CVMX_MIO_FUS_DAT2` and checks fuse fields. Defaults return false for unknown features.

State and persistence: no state is stored except the external `__octeon_feature_bits` cache for crypto. Feature decisions reflect processor ID and immutable fuses at runtime.

Dependencies and integration points: includes `cvmx-mio-defs.h` and `cvmx-rnm-defs.h`; relies on model macros and CSR access from `octeon-model.h`/`cvmx.h`. WQE accessors, PCIe/SRIO/USB setup, interrupt-controller selection, and crypto paths use these probes.

Risks: the function is intended for constant feature arguments so compilers can optimize the switch; nonconstant use is slower. Model tables must stay aligned with hardware support. Fuse reads must be valid on checked families. Incorrect feature answers select wrong WQE layouts, interrupt controllers, or unavailable devices.

Test signals: model-matrix tests should verify each feature against known CN3XXX/CN5XXX/CN6XXX/CN7XXX hardware. Crypto tests should compare `octeon_has_crypto` cached bits with fuse-derived capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon-feature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon-model.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon-model.h

Purpose: defines OCTEON processor model, family, pass/revision, and matching macros used throughout the OCTEON support code.

Important APIs/types/functions: constants define CN3XXX, CN5XXX, CN6XXX, CNF7XXX, and CN7XXX families plus specific model/pass IDs such as CN38XX, CN58XX, CN56XX, CN52XX, CN63XX, CN68XX, CN70XX, CN73XX, CN78XX, CNF71XX, and CNF75XX. Matching flags include ignore revision/minor revision, check submodel, match previous models, and match family groups. Core APIs/macros are `OCTEON_IS_MODEL`, `OCTEON_IS_COMMON_BINARY`, `OCTEON_IS_OCTEON1/PLUS/2/3`, `octeon_model_get_string`, and `cvmx_get_octeon_family`.

Control flow: `OCTEON_IS_MODEL(x)` calls `__octeon_is_model_runtime__`, which reads the processor ID via `cvmx_get_proc_id()` and applies the large `__OCTEON_IS_MODEL_COMPILE__` macro. The matcher handles old CN3XXX revision encoding, newer CN5XXX+ encoding, submodels, pass matching, and family group ranges.

State and persistence: no mutable state. It reads the processor ID register at runtime. `OCTEON_IS_COMMON_BINARY()` is fixed to true in this kernel header, forcing runtime matching rather than compile-time specialization.

Dependencies and integration points: forward-declares `cvmx_get_proc_id` and `cvmx_read_csr`, includes `octeon-feature.h` at the end, and underpins model-gated CSR offsets, WQE layouts, PCIe/USB/SRIO feature checks, and errata workarounds.

Risks: model constants are explicitly internal to this framework and may change; external code should use the macros only. The macro is complex and easy to break with parenthesis or mask edits. Use in preprocessor `#if` is documented as unsupported. Wrong pass matching can select incorrect register layouts or skip errata.

Test signals: unit-style tests can feed synthetic chip IDs into the compile matcher macro, while hardware boot logs should verify `octeon_model_get_string`, family detection, and feature-gated code paths for each supported model/pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon-model.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon.h

Purpose: exposes higher-level OCTEON platform declarations for boot memory allocation, board/bootloader queries, clock setup, delays, boot descriptor layout, and selected CPU control-register bitfields.

Important APIs/types/functions: bootmem APIs include physical/range/named allocation and named free plus lock/unlock declarations. Platform query declarations include simulation, PCI host mode, USB ref clock, clock rates, board type string, PCI interrupts, southbridge interrupt, boot coremask, boot arguments, and user I/O initialization. Timing declarations include CVM count initialization, delay setup, and I/O clock delay. `struct octeon_boot_descriptor` mirrors the bootloader descriptor with endian-specific field ordering, boot flags, core mask, DRAM/clock/board/chip/MAC/serial fields, and descriptor addresses. `union octeon_cvmemctl` models the CvmMemCtl register.

Control flow: this header is mostly declarations and data layout. Boot/board code elsewhere consumes the boot descriptor, performs bootmem allocations, initializes delays/clocks, and configures control-register behavior through the defined bitfields.

State and persistence: boot descriptor data is bootloader-provided and persists in memory for boot-time consumers. Bootmem allocation state is managed externally and can reserve or free named physical memory regions. Control-register fields are live CPU state.

Dependencies and integration points: includes `cvmx.h` and `asm/bitfield.h`. It connects Linux OCTEON platform code with CVMX low-level helpers, bootloader ABI, PCI/USB setup, board identification, and early memory management.

Risks: `struct octeon_boot_descriptor` has fields referenced by assembly and explicitly warns not to reorder early fields. Endian-specific layouts must match the bootloader ABI. Raw physical allocation APIs need alignment/range correctness and locking discipline. Control-register fields affect cache, TLB, sync, and write-buffer behavior.

Test signals: boot tests should validate descriptor parsing, board string/clock/MAC extraction, named bootmem allocation/free, PCI-host query behavior, USB reference-clock detection, and delay calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/pci-octeon.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/pci-octeon.h

Purpose: declares OCTEON-specific PCI/PCIe DMA window constants, IRQ mapping indirection, BAR placement, and DMA BAR type state.

Important APIs/types/functions: `CVMX_PCIE_BAR1_PHYS_BASE`, `CVMX_PCIE_BAR1_PHYS_SIZE`, and `CVMX_PCIE_BAR1_RC_BASE` define the BAR1 physical and root-complex placement. `octeon_pcibios_map_irq` is an extern function pointer used by generic `pcibios_map_irq`. `OCTEON_BAR2_PCI_ADDRESS` defines legacy PCI BAR2 address. `octeon_bar1_pci_phys` holds BAR1 physical mapping for PCI. `enum octeon_dma_bar_type` distinguishes invalid, small, big, PCIe, and PCIe2 DMA mappings. `octeon_dma_bar_type` and `octeon_pci_dma_init()` expose DMA setup state.

Control flow: the header has no inline logic. PCI setup code initializes BAR mappings and DMA type, installs the IRQ mapping callback, and calls `octeon_pci_dma_init` for DMA translation behavior.

State and persistence: global externs hold boot-lifetime PCI mapping state. BAR constants represent hardware address-space layout. No state is persisted beyond runtime.

Dependencies and integration points: includes Linux PCI definitions. It integrates with `pci-octeon.c`, DMA mapping in `dma-octeon.c`, and architecture `pcibios_map_irq`.

Risks: DMA address translation depends on the correct `octeon_dma_bar_type`; a wrong type can produce unreachable or corrupt DMA addresses. IRQ mapping is indirect through a function pointer that must be initialized for PCI versus PCIe host modes. BAR1 hole constants affect available DMA aperture layout.

Test signals: PCI/PCIe enumeration, DMA mapping smoke tests, device IRQ delivery, and BAR1/BAR2 address verification are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/pci-octeon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/paccess.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/paccess.h

Purpose: provides protected MIPS memory access helpers for addresses that may raise instruction or data bus errors, such as optional devices or missing memory.

Important APIs/types/functions: public macros `put_dbe(x, ptr)` and `get_dbe(x, ptr)` wrap size-specific protected access. Internal macros `__get_dbe`, `__get_dbe_asm`, `__put_dbe`, and `__put_dbe_asm` generate inline assembly for 1-, 2-, 4-, and 8-byte loads/stores. Externs include `handle_ibe`, `handle_dbe`, `__get_dbe_unknown`, `__put_dbe_unknown`, and `search_dbe_table`. `__PA_ADDR` selects `.word` or `.dword` exception-table entries by ABI width.

Control flow: a protected access emits an assembly load/store at label 1, sets error to zero on success, and records a fixup target in `__dbe_table`. If a DBE occurs, exception handling searches the table and jumps to the fixup, which sets `-EFAULT`, zeroes a failed load result, and resumes after the access.

State and persistence: no persistent state is maintained by the macros. The compiled binary contains `__dbe_table` metadata used by exception handling. The accessed memory/device can of course have side effects on successful stores.

Dependencies and integration points: includes `linux/errno.h`, uses MIPS exception-table/fixup sections, and integrates with architecture DBE/IBE handlers and `search_dbe_table`.

Risks: only sizes 1, 2, 4, and 8 are supported; other sizes call unknown stubs. Store side effects may partially occur if a bus error happens late. The large fake struct and `"o"` constraints are low-level compiler tricks that must not be casually rewritten. Correct operation requires exception handlers and linker sections to be wired.

Test signals: platform tests should probe valid and invalid device addresses, checking zero return and `-EFAULT` paths. Build tests should cover 32-bit and 64-bit table entry sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/paccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/page.h

Purpose: defines MIPS page-size helpers, huge-page constants, page-table value wrappers, cache-alias handling, physical/virtual address conversion, PFN conversions, KASLR offset access, and memory-model inclusions.

Important APIs/types/functions: `page_size_ftlb` maps Config4 MMU extension definitions and `PAGE_SHIFT` to FTLB page-size encoding. Huge TLB macros define `HPAGE_SHIFT`, `HPAGE_SIZE`, `HPAGE_MASK`, and `HUGETLB_PAGE_ORDER` when enabled, otherwise compile-time traps. Externs include page clear/copy code generators, `ARCH_PFN_OFFSET`, `clear_page`, `copy_page`, `shm_align_mask`, `copy_user_highpage`, `__virt_addr_valid`, and `__kaslr_offset`. Types/macros define `pte_t`, `pgtable_t`, `pgd_t`, `pgprot_t`, `pte_val`, `__pte`, `pgd_val`, `__pgd`, `pgprot_val`, `__pgprot`, `pte_pgprot`, `ptep_buddy`, `__pa`, `__va`, `__pa_symbol`, `pfn_to_kaddr`, `virt_to_pfn`, `virt_to_page`, `virt_addr_valid`, and `kaslr_offset`.

Control flow: `page_size_ftlb` switches on MMU extension mode and panics on invalid configurations. `clear_user_page` clears a page and flushes data cache if virtual aliases differ. `___pa` selects address conversion strategy for MIPS64 compatibility/XKPHYS, standard MIPS32, or EVA. Other macros are direct conversions/wrappers.

State and persistence: no durable state is owned by the header. It reads global architecture state such as `ARCH_PFN_OFFSET`, `shm_align_mask`, cache flush function pointer, and `__kaslr_offset`. Page clear/copy functions mutate page memory.

Dependencies and integration points: includes MIPS spaces, constants, kernel helpers, MIPS registers, vDSO page definitions, PFN helpers, I/O conversions, generic memory model, and getorder. It is foundational for MIPS MM, DMA, page table, and cache-alias code.

Risks: physical/virtual conversion macros are documented for memory initialization only; using them on arbitrary vmalloc/ioremap addresses can be wrong. EVA conversion assumes `PAGE_OFFSET`/`PHYS_OFFSET` mapping. Cache alias flushing depends on `shm_align_mask`. The 64-bit physical-address-on-MIPS32 `pte_t` split layout must be handled through accessors.

Test signals: MM tests should cover FTLB page size encodings, huge-page constants, cache-alias page clear/copy behavior, `virt_addr_valid`, PFN/page conversions, KASLR offset access, and boot-time physical address conversions for supported memory maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/pci.h

Purpose: defines the MIPS architecture PCI interface between board-specific PCI host-controller code and common Linux PCI code.

Important APIs/types/functions: under `CONFIG_PCI_DRIVERS_LEGACY`, `struct pci_controller` holds the controller list node, root bus, OF node, `pci_ops`, memory/I/O resources and offsets, I/O map base, optional domain index/info, and optional bus-number get/set callbacks. Externs include `register_pci_controller`, `pcibios_map_irq`, `pcibios_plat_dev_init`, `pcibios_plat_setup`, `pci_load_of_ranges`, `PCIBIOS_MIN_IO`, and `PCIBIOS_MIN_MEM`. Inline helpers include `set_pci_need_domain_info`, `pcibios_assign_all_busses`, and `pci_proc_domain`; `pci_domain_nr` is defined for non-generic domains. Macros set CardBus minimum I/O and mmap support flags.

Control flow: board code registers controllers before scanning, optionally loads OF ranges, maps IRQs, and performs platform device initialization at enable time. Common PCI scanning asks `pcibios_assign_all_busses`, uses domain helpers, and maps PCI resources using architecture mmap support.

State and persistence: registered `pci_controller` instances are boot-lifetime kernel state in the PCI subsystem. Global minimum I/O/memory values guide resource allocation. Domain info affects procfs/sysfs representation.

Dependencies and integration points: includes Linux MM, ioport, list, OF, types, slab, scatterlist, string, and MIPS I/O helpers. It integrates with board PCI code, Open Firmware device trees, PCI resource allocation, DMA mapping, and arch-specific IRQ mapping.

Risks: legacy-controller definitions are conditional; callers must match `CONFIG_PCI_DRIVERS_LEGACY`. `pcibios_assign_all_busses` always returns 1, forcing bus renumbering and potentially differing from firmware assignments. Domain handling differs between generic and legacy domain configs. The extern `pcibios_plat_dev_init` is declared both inside and outside `__KERNEL__` blocks.

Test signals: PCI host-controller tests should verify controller registration, OF range parsing, bus numbering, domain numbers/proc-domain behavior, resource allocation above `PCIBIOS_MIN_*`, mmap support, IRQ mapping, and platform device init callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pci.h -->
