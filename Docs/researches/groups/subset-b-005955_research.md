# Research: subset-b-005955

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/srp.h -->
# sources/distributed-fs/ceph-client/include/scsi/srp.h

Purpose: defines the wire-format constants and Information Unit layouts for SCSI RDMA Protocol (SRP), including login, command, task management, response, credit, logout, and asynchronous event messages.

Important APIs and types: opcode enums identify SRP request/response IUs; buffer descriptor enums distinguish direct, indirect, immediate, and absent data descriptors. `struct srp_direct_buf`, `struct srp_indirect_buf`, and `struct srp_imm_buf` describe RDMA and immediate data payloads. `struct srp_login_req`, `struct srp_login_req_rdma`, `struct srp_login_rsp`, `struct srp_login_rej`, `struct srp_cmd`, `struct srp_rsp`, `struct srp_tsk_mgmt`, `struct srp_cred_req`, and AER/logout structs model protocol messages. Packed/aligned annotations preserve T10-specified offsets.

Control flow: SRP initiators build login requests, negotiate IU size and descriptor formats, submit SCSI commands with LUN/CDB and descriptor counts, receive `srp_rsp` completions, and manage credits/AER/logout through corresponding IUs. The header has no executable dispatcher; it is consumed by transport drivers when marshalling DMA-visible protocol buffers.

State and persistence: no state is stored here. Runtime protocol state is held by SRP initiator/target drivers, while these structs define transient wire buffers and endian fields.

Dependencies and integration points: depends on Linux scalar types and `struct scsi_lun`. It integrates SRP transports such as RDMA and virtual I/O SCSI with SCSI midlayer command representation.

Risks and test signals: risks are ABI/wire-layout drift, missing byte-order conversion for `__be*` fields, wrong packed alignment on 64-bit builds, descriptor count/format mismatches, and immediate-data offset mistakes. Test with SRP login negotiation, direct/indirect/immediate I/O, task management, logout, sense data responses, credit handling, and compile-time structure-size assertions where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/srp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/viosrp.h -->
# sources/distributed-fs/ceph-client/include/scsi/viosrp.h

Purpose: defines IBM virtual I/O SRP command/response queue formats and management datagrams used by pSeries/iSeries logical partitions to exchange SCSI and SRP management traffic.

Important APIs and types: `union srp_iu` wraps all base SRP IU variants with a 256-byte maximum. `struct viosrp_crq` defines the architected CRQ entry with valid/format/status/timeout/IU length and TCE pointer. Enums describe CRQ headers, init formats, SRP/MAD/OS-specific formats, and CRQ status codes. `struct mad_common` and MAD bodies cover empty IU, error log, adapter info, fast fail, capabilities, reserve, and migration data. `union viosrp_iu` combines SRP and MAD payloads; `struct mad_adapter_info_data` advertises SRP/MAD versions, partition identity, OS type, and per-port transfer limits.

Control flow: virtual SCSI clients place SRP or MAD IUs in DMA buffers, post CRQ entries, process init/complete events, and interpret status for DMA or partner failures. Empty IUs provide a way for the server to respond asynchronously despite the request-oriented flow.

State and persistence: no persistent state is owned here. Hypervisor/driver state includes CRQ rings, DMA mappings, partition capabilities, and outstanding MAD/SRP tags.

Dependencies and integration points: includes `scsi/srp.h` and forms the ABI between Linux and IBM virtual I/O servers, including AIX and OS/400 compatibility.

Risks and test signals: structures are architected and cannot change without cross-OS breakage. Risks include endian errors, CRQ validity/status misinterpretation, MAD length mismatch, capability negotiation regressions, and TCE/IU lifetime bugs. Test virtual SCSI login, init-complete handshake, adapter info, migration/reconnect capabilities, fast-fail enablement, and mixed Linux/AIX/IBM i interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/viosrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/amlogic/meson_ddr_pmu.h -->
# sources/distributed-fs/ceph-client/include/soc/amlogic/meson_ddr_pmu.h

Purpose: declares the Amlogic Meson DDR controller performance-monitor interface used by the DDR PMU platform driver.

Important APIs and types: `MAX_CHANNEL_NUM` and counter IDs define aggregate and per-channel monitor slots. `struct dmc_counter` stores total DDR controller request counts, idle/16-bit/all request variants, and per-channel counters. `struct dmc_hw_info` is the hardware operations table with `enable`, `disable`, AXI filter binding, IRQ counter collection, direct counter reads, controller/channel counts, sysfs format attributes, and capability bits. `struct dmc_info` binds those operations to mapped DDR/PLL registers, timer value, and IRQ. Public entry points are `meson_ddr_pmu_create()` and `meson_ddr_pmu_remove()`.

Control flow: a platform driver creates a PMU instance, programs filters and counters through `dmc_hw_info`, enables sampling, and collects counts either from interrupts or direct reads.

State and persistence: state is runtime-only MMIO mapping, IRQ number, timer period, and accumulated counter snapshots. No firmware or persistent configuration is stored.

Dependencies and integration points: integrates with platform devices, perf/PMU driver code, sysfs attributes, IRQ handling, and SoC-specific DDR controller register layouts.

Risks and test signals: risks include channel count exceeding fixed arrays, mismatched hardware callbacks, filter programming races while counters run, incorrect timer units, and register layout drift between Meson SoCs. Test PMU registration/removal, interrupt sampling, filter selection, all-channel versus per-channel counters, capability exposure, and build coverage for SoC variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/amlogic/meson_ddr_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/arc/arc_aux.h -->
# sources/distributed-fs/ceph-client/include/soc/arc/arc_aux.h

Purpose: abstracts ARC auxiliary register access for code shared between ARC and non-ARC builds.

Important APIs and types: `read_aux_reg()` and `write_aux_reg()` map to ARC compiler builtins under `CONFIG_ARC`; otherwise they compile to harmless stubs. `READ_BCR(reg, into)` and `WRITE_AUX(reg, into)` copy between 32-bit auxiliary register values and typed bitfield structs, deliberately failing link-time through `bogus_undefined()` if sizes do not match.

Control flow: ARC platform code reads build/configuration registers into typed structs, modifies control words, and writes them back through the aux register programming model. Non-ARC users can include the header without introducing architecture-specific instructions.

State and persistence: no independent state exists; helpers read and write processor auxiliary registers, whose state is CPU-local hardware state.

Dependencies and integration points: depends on ARC compiler builtins and is used by MCIP and timer headers to expose register-level programming helpers.

Risks and test signals: risks include passing expressions with side effects into macros, strict-aliasing or layout assumptions in typed copies, non-ARC stub masking accidental runtime use, and wrong bitfield width. Test ARC compile/runtime register reads, non-ARC compile coverage, endian bitfield users, and size mismatch diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/arc/arc_aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/arc/mcip.h -->
# sources/distributed-fs/ceph-client/include/soc/arc/mcip.h

Purpose: defines the ARC Multi-Core IP (MCIP/ARConnect) auxiliary registers, bitfield layouts, command encodings, and inline command helpers for IPI, semaphores, debug, GFRC, and IDU interrupt distribution.

Important APIs and types: register constants cover MCIP build, IDU build, GFRC build, command, write-data, and readback aux registers. `struct mcip_cmd` packs `{cmd,param}` differently for big- and little-endian CPUs. `struct mcip_bcr` and `struct mcip_idu_bcr` expose feature and IRQ-count build-register fields. `mcip_idu_bcr_to_nr_irqs()` converts the IDU exponent encoding. `__mcip_cmd()`, `__mcip_cmd_data()`, and `__mcip_cmd_read()` issue simple, data-bearing, and readback commands.

Control flow: callers optionally write MCIP_WDATA, issue a command through MCIP_CMD, and read MCIP_READBACK for query commands. Comments note callers must lock around data-bearing commands to keep WDATA/CMD atomic.

State and persistence: hardware state includes interrupt pending/ack state, semaphores, debug masks, GFRC selection, and IDU routing. The header stores no software state.

Dependencies and integration points: depends on `arc_aux.h` and integrates SMP/IPI, interrupt controller, timer, and platform bring-up code on ARC systems.

Risks and test signals: risks include missing locking around `__mcip_cmd_data()`, endian bitfield drift, wrong IDU IRQ-count decoding, and using unsupported commands on older MCIP builds. Test SMP IPI generation/ack, IDU enable/mode/destination programming, GFRC reads, semaphore claim/release, big-endian ARC builds, and non-ARC compile guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/arc/mcip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/arc/timers.h -->
# sources/distributed-fs/ceph-client/include/soc/arc/timers.h

Purpose: lists ARC timer auxiliary registers, timer control bits, max counter value, and the timer build-configuration register layout.

Important APIs and types: constants identify TIMER0/TIMER1 limit, control, and count registers. `ARC_TIMER_CTRL_IE` enables interrupt-on-limit and `ARC_TIMER_CTRL_NH` continues counting only when the CPU is not halted. `ARC_TIMERN_MAX` defines the 32-bit limit. `struct bcr_timer` decodes version and timer/RTC/RTSC availability with endian-aware bitfields.

Control flow: clocksource/clockevent code reads `ARC_REG_TIMERS_BCR`, checks available timers, writes limit/control/count registers, and enables interrupting or halt-aware timer behavior.

State and persistence: timer state is per-core hardware counter/control state. No software state or persisted configuration is stored in the header.

Dependencies and integration points: depends on `arc_aux.h`; integrates ARC platform timer drivers and CPU-local auxiliary register access.

Risks and test signals: risks include selecting unavailable timers, using incorrect halt semantics for clocksource accounting, endian bitfield errors, and missing interrupt enable/clear ordering. Test clocksource and clockevent operation on timer0/timer1, suspend/halt behavior, BCR decoding, interrupt delivery, wraparound, and big-endian compile/runtime coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/arc/timers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/at91sam9_ddrsdr.h -->
# sources/distributed-fs/ceph-client/include/soc/at91/at91sam9_ddrsdr.h

Purpose: provides register offsets and bit definitions for Atmel AT91SAM9 DDR/SDR SDRAM controllers.

Important APIs and types: constants define mode, refresh timer, configuration, timing parameter, low-power, memory-device, DLL, high-speed, delay I/O, and write-protection registers. Bitfields cover command modes, column/row bits, CAS latency, DLL reset/disable, off-chip driver, low-power policy, partial array self-refresh, temperature compensation, data bus width, memory type, delay tuning, and write-protect status/source.

Control flow: memory initialization and power-management code programs geometry/timing registers, issues NOP/precharge/load-mode/refresh/normal commands through `MR`, configures low-power behavior, and optionally uses write-protection keys/status while touching controller registers.

State and persistence: controller state is hardware register state affecting live SDR/DDR operation. The header has no software storage; settings are re-established by boot firmware/kernel initialization.

Dependencies and integration points: standalone macro header used by AT91 memory, suspend, and platform code.

Risks and test signals: risks are incorrect timing values, wrong memory-device/width selection, malformed write-protect key use, and accidental deep power-down/self-refresh transitions. Test memory bring-up on SDR/DDR/LPDDR/DDR2 variants, suspend/resume, refresh error behavior, write-protection violation reporting, and register definitions against datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/at91sam9_ddrsdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/at91sam9_sdramc.h -->
# sources/distributed-fs/ceph-client/include/soc/at91/at91sam9_sdramc.h

Purpose: defines register offsets and bit masks for AT91SAM9 SDRAM Controller system peripheral registers.

Important APIs and types: macros cover mode, refresh timer, configuration, low-power, interrupt enable/disable/mask/status, and memory device registers. Fields encode command mode, column/row/bank geometry, CAS latency, data bus width, timing delays, low-power mode, partial array self-refresh, temperature compensation, drive strength, timeout, refresh error status, and SDRAM/low-power SDRAM type.

Control flow: board or memory-controller initialization code writes configuration/timing fields, sequences SDRAM command modes through the mode register, sets refresh, and handles or masks refresh-error interrupts.

State and persistence: only live controller MMIO state is described. Runtime persistence is the configured SDRAM mode until reset/suspend reprogramming.

Dependencies and integration points: standalone header integrated by AT91 platform memory and power-management code.

Risks and test signals: risks include wrong geometry causing aliasing/corruption, invalid timing at changed clock rates, low-power mode misconfiguration, and unhandled refresh errors. Test boot memory sizing, memtest under load, low-power transitions, refresh interrupt paths, and compile coverage for legacy AT91SAM9 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/at91sam9_sdramc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/atmel-secumod.h -->
# sources/distributed-fs/ceph-client/include/soc/at91/atmel-secumod.h

Purpose: defines the minimal Atmel security module register interface needed to check backup/security RAM readiness.

Important APIs and types: `AT91_SECUMOD_RAMRDY` is the RAM ready register offset and `AT91_SECUMOD_RAMRDY_READY` is the ready bit.

Control flow: platform or security-module code maps the syscon/MMIO region and polls or reads `RAMRDY` before using secure/backup RAM.

State and persistence: state is a hardware readiness bit. The header stores no software state and does not persist data.

Dependencies and integration points: uses `BIT()` from common kernel macros through includer context and integrates AT91 security/backup RAM drivers.

Risks and test signals: risks are missing the required include context for `BIT()`, using the RAM before readiness is asserted, and SoC variants with different offsets. Test compile in AT91 configs, boot-time RAM readiness polling, timeout/failure handling, and secure RAM access after readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/atmel-secumod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/atmel-sfr.h -->
# sources/distributed-fs/ceph-client/include/soc/at91/atmel-sfr.h

Purpose: lists Atmel Special Function Register offsets and bit fields used for EBI/DDR, USB, UTMI, light sleep, I2S clock selection, and write protection.

Important APIs and types: offsets include DDR/EBI configuration, OHCI interrupt config/status, UTMI clock trim and DP/DM swap, light sleep, I2S clock selection, and write-protection mode. Macros encode chip select assignment, EBI pull-up/pull-down/drive, NAND-on-D16, DDR multi-port enable, OHCI resume/suspend bits, UTMI trim/swap fields, memory power gating, and write-protect enable/key mask.

Control flow: AT91 platform drivers update SFR syscon registers during pin/memory/USB/suspend initialization, typically through regmap read-modify-write operations and write-protect unlock sequences.

State and persistence: hardware SFR state persists until reset or power-domain loss and affects multiple peripherals. No software state is owned.

Dependencies and integration points: depends on `BIT()`/`GENMASK()` from includers and integrates syscon/regmap clients for AT91 SoC glue.

Risks and test signals: risks include shared register contention, incorrect write-protect key handling, enabling DDR/EBI bits on the wrong SoC, and USB suspend/resume polarity mistakes. Test board boot, NAND/EBI mux, USB host/device operation, suspend light-sleep entry, and regmap write-protect paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/atmel-sfr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/atmel_tcb.h -->
# sources/distributed-fs/ceph-client/include/soc/at91/atmel_tcb.h

Purpose: defines the Atmel Timer/Counter Block shared data structures and register/bit definitions for three-channel TC blocks used by clock, PWM, capture, and timer drivers.

Important APIs and types: `struct atmel_tcb_config` describes counter width, generic clock support, and quadrature decoder support. `struct atmel_tc` tracks the platform device, mapped registers, block id, per-channel IRQs/clocks, slow clock, allocation list node, and allocation flag. `atmel_tc_divisors[]` exposes SoC-specific timer-clock divisors. Macros cover block control/mode registers, external clock routing, channel register addressing, channel control/mode fields, waveform/capture mode settings, counter/RA/RB/RC registers, status bits, interrupt registers, and all IRQ flags.

Control flow: clients allocate a TC block, configure block-wide external clock routing and optional synchronization, configure each channel in capture or waveform mode, enable clocks/IRQs, program compare/capture registers, and read/ack status.

State and persistence: runtime state is MMIO register configuration, enabled clocks/IRQs, driver allocation ownership, and per-channel timer state. No persistent storage is involved.

Dependencies and integration points: depends on platform devices, clocks, lists, and `__iomem`. Integrates clocksource, PWM, input/capture, quadrature, and board-specific timer users.

Risks and test signals: risks include shared block allocation conflicts, IRQ sharing mistakes, wrong clock divisor assumptions, capture/waveform bit overlap misuse, and missed status clear semantics. Test all three channels, shared/per-channel IRQ variants, PWM waveform generation, capture edge modes, block synchronization, clock gating, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/atmel_tcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/sama7-ddr.h -->
# sources/distributed-fs/ceph-client/include/soc/at91/sama7-ddr.h

Purpose: defines Microchip SAMA7 DDR3 PHY and UDDRC register offsets and bit definitions used for DDR initialization and low-power transitions.

Important APIs and types: DDR3PHY definitions include PHY initialization, DLL bypass/lock/reset, clock disable values, initialization-done status, AC/data/power-down controls, ZQ impedance status offsets, and DATX8 DLL disable bits. UDDRC definitions include operating mode/self-refresh status, low-power control, and software/automatic self-refresh controls.

Control flow: DDR setup code resets/initializes PHY DLLs, waits for `PGSR_IDONE`, configures power-down drivers and impedance status, then monitors/controls UDDRC self-refresh and power-down modes.

State and persistence: state is live DDR PHY/controller MMIO state. Incorrect values directly affect memory reliability and power retention; no software state is stored here.

Dependencies and integration points: standalone macro header integrated by SAMA7 DDR initialization, suspend/resume, and SoC power-management code.

Risks and test signals: risks include typo-sensitive bit names, invalid DLL bypass/reset sequencing, insufficient wait for PHY done, wrong self-refresh mode interpretation, and memory loss during low-power entry. Test DDR training/init, suspend/resume with self-refresh, impedance calibration reads, DLL-disable variants, and memory stress across temperature/clock changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/sama7-ddr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/sama7-sfrbu.h -->
# sources/distributed-fs/ceph-client/include/soc/at91/sama7-sfrbu.h

Purpose: exposes SAMA7 backup special-function register offsets and bits for backup power-switch and DDR power state control.

Important APIs and types: under `CONFIG_SOC_SAMA7`, `AT91_SFRBU_PSWBU` identifies the power-switch backup control register; macros define the mandatory write key, state, soft-switch source, and control bits. `AT91_FRBU_DDRPWR` and its state bit expose DDR power mode state.

Control flow: SAMA7 power-management code writes the keyed control register to switch backup power behavior and reads DDR power state during suspend/resume or backup-domain transitions.

State and persistence: hardware backup-domain state may survive portions of system sleep, but this header stores no software state.

Dependencies and integration points: gated by `CONFIG_SOC_SAMA7` and consumed by SAMA7 platform power-management/backup-domain drivers.

Risks and test signals: risks include missing key bits when writing, wrong conditional compile expectations on non-SAMA7 builds, and entering DDR power modes without retention. Test SAMA7 compile, backup power switch state transitions, DDR power-state reads during low power, and resume correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/at91/sama7-sfrbu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/bcm2835/raspberrypi-firmware.h -->
# sources/distributed-fs/ceph-client/include/soc/bcm2835/raspberrypi-firmware.h

Purpose: declares the Raspberry Pi firmware property mailbox interface, property tags, clock IDs, request structs, and optional firmware client APIs.

Important APIs and types: `enum rpi_firmware_property_status` defines request/success/error statuses. `struct rpi_firmware_property_tag_header` describes tag, buffer size, and request/response size. `enum rpi_firmware_property_tag` enumerates board, memory, power, clock, voltage, temperature, GPIO, framebuffer, VCHIQ, DMA, reboot, XHCI, display, OTP, and other mailbox tags. `enum rpi_firmware_clk_id` identifies firmware clocks. `struct rpi_firmware_clk_rate_request` and `RPI_FIRMWARE_CLK_RATE_REQUEST()` encode little-endian clock-rate messages. APIs include `rpi_firmware_property()`, property-list calls, get/put/devm_get, node discovery, and clock max-rate helper, with `-ENOSYS`/NULL/`UINT_MAX` stubs when disabled.

Control flow: drivers obtain a firmware handle, build tag payloads or tag lists, call the firmware property API, interpret status/returned little-endian fields, and release the handle.

State and persistence: firmware state lives on the VideoCore/firmware side and may affect clocks, power domains, framebuffer, OTP, and board state. Kernel state is handle lifetime only.

Dependencies and integration points: depends on OF device nodes, device-managed resources, endian helpers from includers, and mailbox firmware driver support. Integrates clocks, power, framebuffer, USB, GPIO, thermal, and board-info drivers.

Risks and test signals: risks include wrong payload length/alignment, endian conversion mistakes, using stubs as valid firmware, firmware tag compatibility, and mutating persistent OTP/power state unexpectedly. Test property single/list calls, disabled-config stubs, clock rate/max queries, board revision/MAC reads, framebuffer tags, power-domain changes, and error-status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/bcm2835/raspberrypi-firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/canaan/k210-sysctl.h -->
# sources/distributed-fs/ceph-client/include/soc/canaan/k210-sysctl.h

Purpose: provides Kendryte K210 system-controller register offsets and the early clock initialization hook.

Important APIs and types: macros enumerate register offsets for Git ID, UART baud, PLL controllers, PLL lock, ROM error, clock selection, central/peripheral clock enables, soft/peripheral resets, clock thresholds, miscellaneous/peripheral control, SPI sleep, reset status, DMA handshake selectors, and IO power mode. `k210_clk_early_init(void __iomem *regs)` is the public early clock setup entry.

Control flow: early platform code maps SYSCTL, calls `k210_clk_early_init()`, and later clock/reset drivers program PLLs, gates, resets, thresholds, DMA selectors, and power mode registers through these offsets.

State and persistence: SYSCTL MMIO state controls clocks, resets, and power behavior until reset or reprogramming. No software state is held in the header.

Dependencies and integration points: requires `__iomem` context from includers and integrates K210 clock, reset, serial, DMA, and power setup.

Risks and test signals: risks include early init before safe MMIO mapping, PLL lock sequencing, reset register misuse, and register offset drift from vendor SDK assumptions. Test early console clocking, PLL/gate changes, peripheral reset behavior, DMA handshake selection, and build coverage for RISC-V K210 configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/canaan/k210-sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/bman.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/bman.h

Purpose: declares Freescale/NXP BMan buffer descriptor encoding and high-level buffer-pool APIs.

Important APIs and types: `struct bm_buffer` wraps a buffer pool ID plus 48-bit DMA address in an aligned 64-bit hardware word. Inline helpers get/set the DMA address or raw 64-bit address and get/set the 8-bit BPID with big-endian conversion. Opaque `struct bman_portal` and `struct bman_pool` represent portal and pool handles. Public APIs allocate/free pools, query BPID, release/acquire 1-8 buffers, and report BMan/portal probe status.

Control flow: drivers allocate a pool, populate `bm_buffer` entries with DMA addresses and BPID, release buffers to the pool through portal rings, acquire buffers from hardware pools, and free pool objects on teardown.

State and persistence: state is runtime hardware pool contents, portal rings, BPID allocation, and pool objects. Buffer ownership moves between drivers and BMan but is not persistent.

Dependencies and integration points: depends on endian/DMA address helpers from kernel headers and integrates DPAA networking/crypto drivers with BMan portals.

Risks and test signals: risks include 48-bit address truncation, BPID high-bit confusion, releasing non-DMA-safe buffers, ring timeout handling, and probe-order races. Test pool allocation exhaustion, acquire/release counts 1-8, high DMA addresses, portal probe states, timeout paths, and driver teardown with buffers in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/bman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/caam-blob.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/caam-blob.h

Purpose: declares CAAM hardware blob encapsulation/decapsulation support and protected-key metadata.

Important APIs and types: constants define key modifier size, blob overhead, maximum blob length, CCM/ECB protected-key algorithms, nonce/ICV sizes, and CCM overhead. `struct caam_pkey_info` is a packed protected-key header with protected flag, encryption algorithm, plain key size, and flexible key buffer. `struct caam_blob_info` describes input/output DMAable buffers, lengths, key modifier, and embedded protected-key info. APIs include `caam_blob_gen_init()`, `caam_blob_gen_exit()`, `caam_process_blob()`, and inline `caam_encap_blob()`/`caam_decap_blob()` length validators.

Control flow: clients initialize a CAAM blob context, prepare DMAable input/output/key-modifier buffers, call encapsulation or decapsulation, and release the context. The inline wrappers reject impossible output/input sizes before submitting hardware work.

State and persistence: blob context and job-ring resources are runtime state. Produced blobs are persistent encrypted material outside this header; key security depends on CAAM hardware and key modifiers.

Dependencies and integration points: depends on types/errno and integrates trusted key, crypto, NVMEM, or storage users needing CAAM-sealed secrets.

Risks and test signals: risks include non-DMAable buffers, output length underestimation, key modifier length overrun, algorithm/header mismatch, and leaking protected key material. Test init failure without hardware, encap/decap round trips, boundary lengths, invalid key modifiers, DMA mapping errors, and both CCM/ECB protected-key forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/caam-blob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/cpm.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/cpm.h

Purpose: defines common Communication Processor Module and QE parameter-RAM structures, function-code flags, command opcodes, buffer descriptors, protocol status bits, and CPM helper APIs.

Important APIs and types: `struct spi_pram` and `struct usb_ctlr` describe SPI and USB parameter RAM/register blocks. Function-code macros differ for CPM1 versus newer CPM. `cbd_t`/`struct cpm_buf_desc` is the common buffer descriptor with status/control, length, and buffer address. Many `BD_*` macros define serial, Ethernet RX/TX, transparent mode, and I2C status/control bits. `cpm_command()` is available under `CONFIG_CPM` with `-ENOSYS` fallback; `cpm2_gpiochip_add32()` registers CPM2 GPIO support.

Control flow: CPM/QE protocol drivers allocate parameter RAM and buffer descriptor rings, initialize function codes and command opcodes, submit CPM commands, and interpret descriptor ownership/error bits in interrupt or polling paths.

State and persistence: runtime state lives in CPM parameter RAM, BD rings, command engine state, GPIO registration, and DMA buffers. No persistent storage is defined.

Dependencies and integration points: includes QE definitions and kernel OF/types/errno support. Integrates serial, Ethernet, USB, SPI, I2C, and platform GPIO drivers on CPM/QE SoCs.

Risks and test signals: risks include endian/packing mistakes, descriptor ownership races, CPM1/CPM2 flag differences, command opcode aliasing, and wrong buffer address width. Test protocol TX/RX rings, error status handling, CPM disabled stubs, GPIO registration, and CPM1/CPM2/QE config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/cpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/dcp.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/dcp.h

Purpose: defines protected-AES key slot handles for NXP MXS DCP crypto users.

Important APIs and types: `DCP_PAES_KEYSIZE` marks the one-byte protected-key handle size. Slot constants identify hardware key slots 0-3, the device-unique key, and OTP key handles for `crypto_skcipher_setkey()` style use.

Control flow: crypto clients select a protected key by passing one of these handles as the key material to DCP-backed AES operations.

State and persistence: key material itself resides in DCP hardware/OTP/unique key sources. The header only defines selector values and stores no state.

Dependencies and integration points: standalone header integrated with the MXS DCP crypto driver and protected-key consumers.

Risks and test signals: risks include treating one-byte handles as raw AES keys, accepting invalid slot values, and mismatched userspace/key-management expectations. Test PAES setkey with each supported slot, invalid handle rejection, OTP/unique key behavior, and disabled/non-DCP build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/dcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-fd.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-fd.h

Purpose: provides DPAA2 Frame Descriptor, scatter-gather entry, and frame-list entry layouts plus inline accessors for DPAA2 datapath hardware.

Important APIs and types: `struct dpaa2_fd` is the 32-byte frame descriptor with address, length, BPID, format/offset, frame context, control, and flow context. Masks define short-length, format, offset, BPID, final, and error/annotation bits. `enum dpaa2_fd_format`, `struct dpaa2_sg_entry` with `enum dpaa2_sg_format`, and `struct dpaa2_fl_entry` with `enum dpaa2_fl_format` describe single, SG, and frame-list forms. Inline helpers get/set addresses, lengths, offsets, formats, BPIDs, FRC, CTRL, FLC, final flags, and short-length behavior with little-endian conversion.

Control flow: DPAA2 drivers build descriptors, enqueue them to frame queues, dequeue and parse them, walk SG tables or frame lists, and use control/error bits to route completion/error handling.

State and persistence: descriptors are transient DMA-visible memory owned by drivers/hardware queues. No persistent state is stored.

Dependencies and integration points: depends on Linux types and byteorder helpers; integrates DPIO, Ethernet, crypto, and accelerator drivers.

Risks and test signals: risks include incorrect endian updates during read-modify-write, unmasked offsets/BPIDs/lengths, final-bit errors in SG/FLE chains, short-length interpretation drift, and DMA address truncation on unusual platforms. Test descriptor encode/decode round trips, SG final handling, frame-list queues, FD error bits, high DMA addresses, and compile-time layout/size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-fd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-global.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-global.h

Purpose: defines DPAA2 dequeue result and congestion notification formats plus helpers for parsing queue manager responses.

Important APIs and types: `struct dpaa2_dq` overlays common, frame dequeue, and state-change notification layouts. Status flags report empty, held-active, force-eligible, valid frame, ODP-valid, volatile dequeue, and expired completion. Helpers parse flags, pull/static dequeue identity, pull completion, sequence number, ODP id, FQID, byte/frame counts, frame queue context, embedded `struct dpaa2_fd`, and congestion state in CSCNs. Constants define CSCN size/alignment and congestion bit.

Control flow: DPIO store/poll code obtains dequeue entries, checks flags for valid frames and pull completion, extracts queue metadata and FD, and handles congestion state notifications.

State and persistence: dequeue results are transient hardware response records. Queue counters and congestion state live in QMan/DPIO hardware.

Dependencies and integration points: includes DPAA2 FD definitions, types, and cpumask headers. Used by DPIO services and DPAA2 Ethernet/accelerator consumers.

Risks and test signals: risks include reading invalid fields without required status bits, FQID/frame-count mask mistakes, embedded FD alignment assumptions, and stale congestion notifications. Test pull and static dequeue, empty versus valid entries, expired pull completion, congestion entry/exit, and FD extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-io.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-io.h

Purpose: declares the DPAA2 DPIO service API for creating portals, handling notifications, enqueueing/dequeueing frame descriptors, buffer pool operations, stores, queue counts, and IRQ coalescing.

Important APIs and types: `struct dpaa2_io_desc` describes a portal, notification support, priority mode, CPU affinity, register mappings, DPIO id, QMan version, and clock. `struct dpaa2_io_notification_ctx` holds callbacks, CDAN/FQDAN identity, target CPU/DPIO id, QMan context, list node, and private data. APIs create/down DPIO objects, handle IRQs, select per-CPU services, register/deregister/rearm notifications, pull FQs/channels into stores, enqueue single/multiple descriptors to FQ/QD, acquire/release buffers, create/destroy/iterate stores, query FQ/BP counts, and tune IRQ coalescing/adaptive DIM.

Control flow: drivers select or create a DPIO service, register notification callbacks, pull work into stores, iterate `dpaa2_dq` results, enqueue completions/frames, and manage buffer pools through acquire/release.

State and persistence: runtime state includes portal mappings, notification lists, stores, interrupt/coalescing settings, and hardware queue state. No persistent storage is defined.

Dependencies and integration points: depends on DPAA2 FD/global headers, IRQ types, devices, cpumask, and list users. It is the core service layer for DPAA2 networking and accelerators.

Risks and test signals: risks include CPU affinity mismatch, notification rearm races, store exhaustion, enqueue batching partial failures, buffer-count overflows, and IRQ coalescing regressions. Test portal probe/teardown, FQ/channel pulls, notification callbacks, multi-enqueue paths, buffer acquire/release, query counts, and coalescing updates under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/immap_qe.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/qe/immap_qe.h

Purpose: defines the QUICC Engine internal memory map as packed C structs matching the SoC MMIO layout.

Important APIs and types: `QE_IMMAP_SIZE` covers the 1 MiB QE block. Structs model I-RAM, interrupt controller, communications processor, mux, timers, BRG, SPI, SI, SI RAM routing tables, USB, MCC, UCC slow/fast register blocks, generic UCC slots, UPC controllers, SDMA, debug space, RISC special registers, and the top-level `struct qe_immap`. `extern struct qe_immap __iomem *qe_immr` exposes the mapped base.

Control flow: QE platform code maps the IMMR/QE region into `qe_immr`, then drivers access typed substructures for register programming, microcode upload, timers, UCC protocols, SDMA, and routing tables.

State and persistence: all represented fields are live MMIO/hardware state. Some MURAM contents hold parameter RAM or buffer descriptors during runtime but are not persistent across reset.

Dependencies and integration points: gated by `__KERNEL__`, depends on big-endian MMIO types and `asm/io.h`, and is used by QE, CPM, UCC, TDM, USB, Ethernet, serial, and SDMA drivers.

Risks and test signals: risks include struct packing/offset drift, SoC variant register differences, direct MMIO access without ordering, and mismatched endian accessors. Test register offset assertions where available, QE boot/probe, UCC fast/slow drivers, microcode upload, MURAM access, and compile coverage on PowerPC QE SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/immap_qe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/qe.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/qe/qe.h

Purpose: exposes QUICC Engine common services, MURAM allocation, parallel I/O, pin muxing, command issuance, clock/BRG management, firmware format, buffer descriptors, and QE register bit definitions.

Important APIs and types: `enum qe_clock`, `qe_clock_is_brg()`, `qe_reset()`, MURAM alloc/free/address/DMA helpers and QE aliases, `struct qe_pio_regs`, parallel I/O APIs, QE GPIO pin APIs, `qe_issue_cmd()`, BRG/SNUM/RISC discovery APIs, `qe_alive_during_sleep()`, register set/clear macros, `struct qe_firmware` and `struct qe_firmware_info`, `qe_upload_firmware()`, `qe_get_firmware_info()`, `qe_usb_clock_set()`, and `struct qe_bd`. Numerous macros define alignment, RISC allocation, filtering table descriptors, communication direction, CMX routing, CECR commands/subblocks/protocols, BRG, timers, SDMA, CP, IRAM, UPC, GUEMR, UCC mode, event, and bus/function-code bits.

Control flow: platform code initializes MURAM/QE, configures pins/clocks/BRGs, uploads firmware if needed, allocates parameter RAM/BDs, and protocol drivers issue QE commands and manipulate UCC/MURAM resources.

State and persistence: runtime state includes QE registers, MURAM allocator state, SNUM allocation, firmware/microcode state, PIO mux state, and buffer descriptors. No filesystem persistence is handled here.

Dependencies and integration points: includes CPM and QE memory-map headers, OF/address helpers, genalloc, spinlocks, and device APIs. It is the central integration point for QE users.

Risks and test signals: risks include disabled-config stubs returning `-ENOSYS`, MURAM lifetime leaks, pinmux conflicts, command subblock/protocol mistakes, endian MMIO misuse, firmware format incompatibility, and sleep behavior differences on PPC85xx. Test QE probe/reset, MURAM alloc/free/fixed/devm paths, BRG rate setting, SNUM exhaustion, firmware upload/CRC consumers, pinmux from device tree, and UCC protocol bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/qe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/qe_tdm.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/qe/qe_tdm.h

Purpose: declares QE TDM mode data structures, SI RAM entry bits, SI mode fields, and setup helpers for UCC TDM users.

Important APIs and types: SI RAM macros define last/byte/count/channel-select/superframe/software-trigger/MCC/idle entries. SIxMR macros configure start address, normal/internal-loopback mode, clock/edge/gate bits, and TX/RX frame sync delay. Enums describe TX/RX timeslot direction, T1/E1 framer type, and normal/internal-loopback mode. `struct si_mode_info` holds decoded SI mode fields. `struct ucc_tdm_info` combines `ucc_fast_info` with SI settings. `struct ucc_tdm` tracks TDM port, SI RAM entry, mapped SI RAM/registers, framer/mode, timeslot count, and TX/RX masks. APIs parse DT and initialize TDM.

Control flow: a UCC TDM driver parses device-tree TDM properties, fills SI mode/UCC settings, programs SI RAM and SI registers, then initializes the UCC fast path for TDM traffic.

State and persistence: state is runtime SI RAM/register programming and `ucc_tdm` software bookkeeping. No persistent state is stored.

Dependencies and integration points: includes QE memory map, QE core, UCC, and UCC fast headers; integrates TDM-framed serial/network drivers with QE SI routing.

Risks and test signals: risks include incorrect timeslot masks, off-by-one SI RAM entries, T1/E1 framing mismatch, loopback mode leakage, and device-tree parse errors. Test T1/E1 configurations, TX/RX masks, loopback, SI RAM programming, UCC fast initialization, and start/stop under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/qe_tdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/qmc.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/qe/qmc.h

Purpose: declares the QE QMC channel consumer API for obtaining channels, configuring modes/timeslots, submitting DMA reads/writes, and controlling channel direction.

Important APIs and types: phandle helpers count and get `struct qmc_chan` by phandle index, single phandle, or child node, with devm variants and `qmc_chan_put()`. `enum qmc_mode` supports transparent and HDLC. `struct qmc_chan_info` reports mode, frame sync rates, bit rates, and TX/RX timeslot counts. `struct qmc_chan_ts_info` reports available and selected TX/RX timeslot masks. `struct qmc_chan_param` configures transparent or HDLC buffer/frame sizes and CRC32. Read flags report HDLC last/first/overflow/unaligned/abort/CRC errors. APIs submit write/read DMA buffers with completion callbacks and start/stop/reset read/write/all directions.

Control flow: client drivers acquire channels from DT, inspect capabilities, configure timeslots and mode parameters, submit DMA buffers, process async completions, and start/stop/reset directions as link state changes.

State and persistence: runtime state includes channel ownership, mode/TS configuration, queued DMA buffers, and active direction state. No persistent storage is owned.

Dependencies and integration points: depends on DT/device/types/bits and integrates QMC providers with HDLC/transparent serial or telecom drivers.

Risks and test signals: risks include missing `qmc_chan_put()`, invalid timeslot masks, callback lifetime after stop/reset, DMA buffer ownership confusion, and HDLC flag interpretation. Test phandle lookup/devm cleanup, transparent and HDLC modes, CRC32 selection, read/write completion ordering, stop/reset with in-flight buffers, and timeslot reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/qmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc.h

Purpose: declares common UCC utility APIs for selecting fast/slow mode and configuring QE mux clock/routing features.

Important APIs and types: `UCC_MAX_NUM` defines eight UCCs. `enum ucc_speed_type` maps fast/slow selections to GUEMR RX/TX mode bits. APIs include `ucc_set_type()`, `ucc_set_qe_mux_mii_mng()`, `ucc_set_qe_mux_rxtx()`, `ucc_set_tdm_rxtx_clk()`, `ucc_set_tdm_rxtx_sync()`, and `ucc_mux_set_grant_tsa_bkpt()`. Inline wrappers set grant, TSA, and breakpoint bits through the shared mux helper.

Control flow: protocol drivers configure a UCC as fast or slow, route clocks/sync signals for TX/RX, optionally set MII management routing, and enable grant/TSA/breakpoint mux bits before protocol-specific initialization.

State and persistence: state is QE mux/GUEMR hardware configuration and no persistent software state.

Dependencies and integration points: includes QE memory-map/core headers and uses `enum qe_clock` and `enum comm_dir`. It is shared by UCC fast, slow, Ethernet, serial, and TDM users.

Risks and test signals: risks include invalid UCC numbers, mux conflicts between protocols, wrong direction clock routing, and missing synchronization around shared CMX registers. Test each UCC index, fast/slow transitions, MII management muxing, TDM clock/sync routing, and concurrent configuration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc_fast.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc_fast.h

Purpose: declares Fast UCC status bits, configuration enums, private state, and lifecycle/control APIs for high-speed QE protocol channels.

Important APIs and types: macros define 32-bit and 16-bit RX/TX buffer descriptor ownership, wrap, interrupt, first/last, continuous, and error bits. Alignment and FIFO sizing constants constrain buffers and virtual FIFO registers. Enums configure protocol mode, transparent TX/RX, diagnostic mode, sync length, RTS behavior, NRZ/NRZI encoding, and CRC length. `struct ucc_fast_info` carries UCC/TDM number, clocks/syncs, registers, IRQ, mask, mux flags, FIFO sizes, max RX length, protocol mode, encoding, CRC, and sync length. `struct ucc_fast_private` tracks mapped registers/event/mask pointers, enabled/stopped state, FIFO MURAM offsets, optional stats, and MRBLR. APIs initialize/free, enable/disable directions, handle IRQs, transmit-on-demand, compute command subblocks, and dump registers.

Control flow: callers fill `ucc_fast_info`, initialize resources and FIFOs, enable RX/TX, handle interrupts, optionally force TX polling, then disable/free on teardown.

State and persistence: runtime state includes hardware registers, MURAM FIFO allocations, enabled/stopped flags, event masks, and optional counters. No persistent data.

Dependencies and integration points: includes QE, immap, and common UCC headers; used by fast protocols such as Ethernet, HDLC/POS/ATM, and TDM users.

Risks and test signals: risks include FIFO alignment/size mistakes, BD status width confusion, stale enabled/stopped flags, command subblock mismatch, and IRQ mask loss. Test initialization failure unwinding, TX/RX enable/disable, IRQ paths, transmit-on-demand, each protocol mode used by drivers, and MURAM leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc_fast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc_slow.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc_slow.h

Purpose: declares Slow UCC descriptor bits, configuration enums, private state, and lifecycle/control APIs for lower-speed QE serial protocols.

Important APIs and types: TX/RX BD macros cover ready/empty, wrap, interrupt, first/last, address/control, CRC, continuous, preamble, heartbeat, underrun, CTS/carrier/collision, frame length, non-octet, parity, abort, CRC, overrun, and address-match conditions. Alignment constants define RX/MRBLR/parameter-RAM constraints. Enums configure QMC/UART/BISYNC mode, transparent CRC, TX/RX oversampling, NRZ/NRZI encoding, and diagnostic loopback/echo. `struct ucc_slow_info` carries UCC number, protocol, clocks, register address, IRQ, masks, BD ring lengths, mux flags, inversion/encoding/timing options, max RX length, CRC, mode, and diagnostics. `struct ucc_slow_private` tracks mapped registers/pram, BD rings, queue/list state, event/mask pointers, saved mask, enabled/stopped flags, RX accumulation, and optional stats. APIs initialize/free, enable/disable, graceful/force stop TX, restart TX, and compute command subblocks.

Control flow: a protocol driver initializes parameter RAM and BD rings, enables selected directions, processes RX/TX BDs and events, uses QE commands for stop/restart, then frees resources.

State and persistence: state is runtime parameter RAM, BD rings in MURAM, queued TX confirmations, RX accumulation, event masks, and counters. No persistent data.

Dependencies and integration points: includes QE/immap/common UCC headers and list support via included structures. Used by UART, BISYNC, QMC, and related slow protocols.

Risks and test signals: risks include BD flag aliasing across protocols, ring wrap errors, RX frame accumulation leaks, stop/restart races, parameter RAM alignment mistakes, and missed IRQ masking. Test UART/QMC/BISYNC configurations, RX/TX rings, graceful/force stop, restart, error BD handling, and teardown with queued frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc_slow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qman.h -->
# sources/distributed-fs/ceph-client/include/soc/fsl/qman.h

Purpose: declares Freescale/NXP QMan hardware descriptor formats and the high-level portal, frame queue, congestion group, resource allocation, dequeue, enqueue, and coalescing APIs.

Important APIs and types: constants define channel IDs, interrupt sources, static dequeue pool masks, descriptor masks, FQ/CGR write-enable flags, and volatile dequeue flags. `struct qm_fd` and helpers encode 40-bit frame addresses, formats, offsets, and lengths. `struct qm_sg_entry` models SG entries. `struct qm_dqrr_entry` and `union qm_mr_entry` model dequeue and message-ring responses. `struct qm_fqd`, stashing/OAC helpers, taildrop helpers, `struct __qm_mc_cgr`, CGR threshold helpers, `struct qm_mcc_initfq`, and `struct qm_mcc_initcgr` build management commands. `struct qman_fq` and `struct qman_cgr` are caller-visible objects with dequeue/message/congestion callbacks. APIs manage portal IRQ sources, polling/static dequeue, FQ lifecycle, volatile dequeue, enqueue, FQID/pool/CGRID allocation, CGR lifecycle/query, probe status, and DQRR interrupt coalescing.

Control flow: drivers create/init/schedule FQs, enqueue `qm_fd` descriptors, receive DQRR callbacks, process ERN/FQ state messages, retire/OOS/destroy queues, and optionally use CGRs for congestion notifications. Portal code switches between interrupt-driven and polled sources and manages affine channels.

State and persistence: runtime state spans QMan portals, FQ objects, hardware FQD/CGR tables, ring entries, resource allocators, congestion state, and callback registrations. No persistent storage is defined.

Dependencies and integration points: depends on bitops, device/cpumask/list users, endian helpers from includers, and DPAA BMan/FMan/CAAM consumers. It is central to DPAA packet processing.

Risks and test signals: risks include 40-bit DMA address truncation, FQ state-machine races, callback reentrancy during retire, portal affinity misuse, taildrop/CGR threshold rounding errors, message-ring consumption bugs, and resource ID leaks. Test FQ create/init/schedule/enqueue/dequeue/retire/OOS/destroy, volatile dequeue completion, ERN paths, CGR congestion callbacks, resource allocator exhaustion/release, coalescing settings, and high-address descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/fsl/qman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/imx/cpu.h -->
# sources/distributed-fs/ceph-client/include/soc/imx/cpu.h

Purpose: provides i.MX/Vybrid CPU type numeric identifiers and exposes the global detected CPU type.

Important APIs and types: macros define legacy MX1/MX2/MX3/MX5, i.MX6/i.MX7, and Vybrid CPU IDs, including composite VF510/VF610 values and a virtual i.MX6ULZ ID. Outside assembly, `extern unsigned int __mxc_cpu_type` provides the detected type.

Control flow: platform code sets `__mxc_cpu_type` during early SoC detection and drivers/board code compare it against these macros to select quirks or capabilities.

State and persistence: `__mxc_cpu_type` is runtime global kernel state initialized from hardware/boot data. It is not persistent.

Dependencies and integration points: assembly-safe macro header integrated by i.MX platform and driver quirk code.

Risks and test signals: risks include stale ID comparisons, duplicate/virtual IDs, and using CPU type where device tree compatibles would be safer. Test early SoC detection, quirk selection on each supported family, assembly include compatibility, and compile coverage for ARM i.MX/Vybrid configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/imx/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/imx/cpuidle.h -->
# sources/distributed-fs/ceph-client/include/soc/imx/cpuidle.h

Purpose: declares i.MX6Q CPU-idle hooks used by FEC/networking paths to indicate whether Ethernet IRQs are in use.

Important APIs and types: when both `CONFIG_CPU_IDLE` and `CONFIG_SOC_IMX6Q` are enabled, `imx6q_cpuidle_fec_irqs_used()` and `imx6q_cpuidle_fec_irqs_unused()` are external functions. Otherwise they compile to no-op inline stubs.

Control flow: FEC or platform code calls the hooks when Ethernet IRQ usage changes so the i.MX6Q cpuidle implementation can avoid low-power states that would break wake/interrupt behavior.

State and persistence: state is maintained by the cpuidle implementation, likely runtime counters/flags. The header stores none.

Dependencies and integration points: integrates i.MX6Q cpuidle with FEC/network drivers while allowing builds without CPU idle or i.MX6Q support.

Risks and test signals: risks include unbalanced used/unused calls, no-op stubs hiding missing power constraints on unsupported configs, and regressions in wake from Ethernet. Test FEC open/close, suspend/idle with active Ethernet IRQs, disabled-config builds, and repeated interface up/down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/imx/cpuidle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/imx/revision.h -->
# sources/distributed-fs/ceph-client/include/soc/imx/revision.h

Purpose: defines i.MX silicon revision constants and revision query/printing APIs.

Important APIs and types: macros encode revisions 1.0 through 3.3 and unknown as compact hex values. Functions query specific MX25/MX27/MX31/MX35/MX51/MX53 revisions, return generic SoC revision via `imx_get_soc_revision()`, and print silicon revision strings with `imx_print_silicon_rev()`.

Control flow: platform initialization detects SoC revision, stores it in platform state, and drivers call revision helpers to apply errata or report silicon versions.

State and persistence: detected revision is runtime platform state derived from hardware fuses/registers. No persistent state is stored by the header.

Dependencies and integration points: used by i.MX platform/driver errata handling and boot logging.

Risks and test signals: risks include treating `UNKNOWN` as a valid comparable revision, applying errata to wrong families, and missing helper implementations in configs. Test revision reads on supported SoCs, boot log formatting, errata quirk paths, and compile/link coverage for all declared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/imx/revision.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mediatek/smi.h -->
# sources/distributed-fs/ceph-client/include/soc/mediatek/smi.h

Purpose: exposes MediaTek SMI/IOMMU integration definitions for local arbiter IOMMU configuration.

Important APIs and types: under `CONFIG_MTK_SMI`, `enum iommu_atf_cmd` defines secure monitor commands to configure SMI LARB or infra IOMMU. `MTK_SMI_MMU_EN(port)` builds an enable bit for a port. `struct mtk_smi_larb_iommu` records a LARB device, MMU bitmask, and per-port bank mapping.

Control flow: MediaTek IOMMU/SMI code associates LARB devices with ports/banks, computes MMU enable bits, and may issue ATF commands to enable or disable IOMMU paths for multimedia or infrastructure masters.

State and persistence: runtime state is LARB device association, MMU masks, bank routing, and secure firmware configuration. No persistent storage is managed.

Dependencies and integration points: depends on bitops and device headers and is compiled only for MediaTek SMI users. Integrates IOMMU, SMI bus, multimedia, and ATF firmware paths.

Risks and test signals: risks include missing declarations when `CONFIG_MTK_SMI` is disabled, wrong port-to-bank mapping, secure firmware command mismatch, and enabling untranslated DMA. Test LARB probe, IOMMU attach/detach, per-port enable bits, multimedia DMA under IOMMU, and disabled-config compile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mediatek/smi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/microchip/mpfs.h -->
# sources/distributed-fs/ceph-client/include/soc/microchip/mpfs.h

Purpose: declares Microchip PolarFire SoC system-controller message structures and optional sys-controller, flash, and reset-controller APIs.

Important APIs and types: `struct mpfs_mss_msg` describes a mailbox transaction with opcode, command size/data, response pointer, mailbox offset, and response offset. `struct mpfs_mss_response` holds status, response words, and response size. When `CONFIG_POLARFIRE_SOC_SYS_CTRL` is enabled, APIs perform blocking transactions, get the sys-controller handle, and get flash. When MPFS clock and reset controller configs are enabled, `mpfs_reset_controller_register()` registers reset support; otherwise a stub returns success.

Control flow: clients acquire the system controller, prepare mailbox command/response buffers and offsets, perform blocking transactions to MSS firmware, and optionally register reset control from the clock driver.

State and persistence: runtime state includes sys-controller client handles, mailbox firmware state, response buffers, flash handle, and reset regmap state. Firmware/flash contents persist outside this header.

Dependencies and integration points: depends on OF device, regmap, and MTD/reset/clock users. Integrates MPFS MSS services with platform drivers.

Risks and test signals: risks include absent fallback declarations for disabled sys-controller users, mismatched reset stub signature versus enabled signature, mailbox offset/size errors, blocking transaction hangs, and firmware status misinterpretation. Test sys-controller probe, transaction success/failure/timeouts, flash access, reset registration across config matrices, and invalid command sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/microchip/mpfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot.h -->
# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot.h

Purpose: declares the Microsemi/Microchip Ocelot switch core register namespace, state structures, regmap helpers, packet I/O, switching, timestamping, QoS, devlink, phylink, VCAP, MRP, MAC Merge, and platform operations.

Important APIs and types: PGID constants/macros define L2 destination, aggregation, and source masks. `enum ocelot_target`, `enum ocelot_reg`, and `enum ocelot_regfield` enumerate switch targets, registers, counters, and regfields. `struct ocelot_ops` supplies platform callbacks for port mapping, reset, watermarks, PSFP, cut-through, TAS, and stats. State structs cover VCAP policers/blocks, bridge VLANs, PSFP lists, LAG FDBs, mirroring, MAC Merge state, timestamp stats, `struct ocelot_port`, and top-level `struct ocelot`. Macros wrap indexed regmap reads/writes/RMW and target reads/writes. Function declarations cover I/O, injection/extraction, PTP RX/TX timestamps, reset/init/deinit, DSA 802.1Q CPU ports, stats, VLAN/bridge/STP/FDB/MDB/LAG, hardware timestamping, policing/mirroring/flower, devlink shared buffers, SerDes/phylink, MAC table stream data, VCAP policers, MAC Merge, mqprio, optional MRP, and PLL init.

Control flow: platform drivers fill `struct ocelot`, initialize regmaps/regfields, reset/init ports, then switchdev/DSA/phylink/ethtool/TC callbacks manipulate bridge, VLAN, FDB, QoS, timestamp, and packet I/O state through these helpers.

State and persistence: runtime state is extensive: port objects, register maps, VLAN/trap/LAG/VCAP/PSFP lists, stats workqueues, locks, timestamp queues, PTP clock, MAC Merge state, FDMA, and hardware tables. It is rebuilt on probe, with no file persistence.

Dependencies and integration points: depends on networking, DSA, PTP, timestamping, VLAN, regmap, devlink, switchdev, phylink, TC flower/mqprio/taprio, and optional bridge MRP support.

Risks and test signals: risks include PGID forwarding-mask corruption, indexed register offset mistakes, lock-order issues among injection/extraction/stats/MAC table/PTP, stale FDB/VLAN/LAG state, timestamp skb leaks, optional MRP stubs returning `-EOPNOTSUPP`, and config drift across Ocelot/Felix variants. Test bridge/VLAN/FDB/MDB/LAG offload, DSA CPU tagging, PTP RX/TX, packet injection/extraction, ethtool stats, devlink SB, TC flower/PSFP/TAS/mqprio, MAC Merge, phylink speed modes, MRP enabled/disabled, and reset/deinit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot.h -->
