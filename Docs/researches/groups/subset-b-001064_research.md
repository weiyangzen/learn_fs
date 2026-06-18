# subset-b-001064 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btintel.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btintel.c

## Purpose
Provides the common Intel Bluetooth controller support used by transports such as USB and PCIe. It owns Intel vendor HCI command helpers, legacy and TLV version parsing, firmware and DDC download flows, boot and reset handshakes, diagnostics and devcoredump hooks, ACPI/UEFI platform policy handling, SAR/PPAG/DSBR configuration, and the combined setup/shutdown callbacks installed on `struct hci_dev`.

## Important APIs, Types, And Functions
- Exported setup and operation entry points include `btintel_configure_setup`, `btintel_shutdown_combined`, `btintel_recv_event`, `btintel_hw_error`, `btintel_set_bdaddr`, `btintel_set_diag`, `btintel_set_quality_report`, `btintel_set_msft_opcode`, and `btintel_print_fseq_info`.
- Firmware entry points include `btintel_read_version`, `btintel_read_boot_params`, `btintel_download_firmware`, `btintel_bootloader_setup_tlv`, `btintel_bootup`, and `btintel_secure_send_result`.
- Version and firmware data structures come from `btintel.h`: `struct intel_version`, `struct intel_version_tlv`, `struct intel_boot_params`, `struct intel_reset`, `struct intel_debug_features`, and SAR/DDC command structs.
- Internal helpers split secure firmware headers by RSA, ECDSA, or hybrid ECDSA+LMS format, stream aligned payload fragments through opcode `0xfc09`, parse `CMD_WRITE_BOOT_PARAMS`, select firmware names, and apply DDC records through opcode `0xfc8b`.
- `btintel_regmap_init` exposes an HCI-command-backed regmap bus for transports that need register-like access over Intel vendor opcodes.

## Control Flow
Combined setup starts in `btintel_setup_combined`. It may send an initial HCI reset for controllers with broken command credits or shutdown LED state, then issues Intel Read Version (`0xfc05`) with the TLV selector. Legacy responses are routed to legacy ROM patching or legacy bootloader setup; TLV responses are validated, quirked, and routed to `btintel_bootloader_setup_tlv`. Legacy ROM patching enters manufacturing mode, replays a `.bseq` stream of expected command/event pairs, and exits manufacturing mode with or without reset/patch activation. Bootloader setup requests `.sfi` firmware, sends secure header fragments and aligned data fragments, waits for a firmware-download vendor event, sends Intel reset to boot the loaded image, waits for bootup, applies `.ddc`, and enables Intel event masks.

The TLV boot path can perform a two-stage load. It downloads IML or operational firmware based on `img_type`, reads a fresh TLV version after the first boot, applies DSBR if the product/transport requires it, optionally downloads the second image, then applies DDC, SCO offload callbacks, SAR, PPAG, MSFT extension opcode, and final version logging. Vendor events are intercepted by `btintel_recv_event`: bootloader firmware-download events clear `INTEL_DOWNLOADING`, bootup events clear `INTEL_BOOTING`, diagnostics events can become devcoredumps, and all other events fall through to `hci_recv_frame`.

## State And Persistence
Persistent driver state is mostly in `struct btintel_data` attached as HCI private data. Its bitmap tracks `INTEL_BOOTLOADER`, `INTEL_DOWNLOADING`, `INTEL_FIRMWARE_LOADED`, `INTEL_FIRMWARE_FAILED`, `INTEL_BOOTING`, legacy ROM quirks, ACPI reset state, and `INTEL_WAIT_FOR_D0`. These flags are used as wait-bit synchronization points between setup code and vendor event receive paths. `coredump_info` caches driver name, hardware variant, and firmware build for common devcoredump headers. Firmware and DDC blobs are requested from the firmware loader and released after use. ACPI reset method selection persists as `btintel_data.acpi_reset_method`; ACPI/UEFI values are read on demand and not written back by this file.

## Dependencies And Integration Points
The file depends on Bluetooth HCI core command synchronization, HCI quirk and callback registration, firmware loading, regmap, ACPI DSM/_PRR/_RST methods, EFI runtime variables, device coredump support, and Intel vendor HCI opcodes. Transports call these helpers directly or install them through `btintel_configure_setup`; the PCIe transport additionally depends on the shared boot flags and event helpers while supplying its own receive/event path. Firmware artifacts live under `intel/*.sfi`, `intel/*.ddc`, and legacy `intel/*.bseq` names selected from hardware version fields.

## Risks And Edge Cases
Firmware parsing assumes command headers and fragment alignment inside untrusted firmware files; malformed sizes or missing boot-parameter commands can abort setup. The version matrix is conservative, so new hardware variants fail until enumerated. Timeout-driven waits depend on vendor events being consumed by the transport receive path; missed boot/download events leave setup blocked until timeout. PCIe skips USB-style reset-to-bootloader recovery, so transport reset must cover those failures. ACPI package parsing for PPAG/SAR assumes exact package shape after minimal validation, and SAR/DDC writes are policy-sensitive. The static `coredump_info` is shared across devices, which is acceptable for typical controller counts but can blur metadata in multi-device cases.

## Test Signals
Useful tests include default Intel BDADDR detection, legacy `.bseq` replay with expected event mismatch, missing and malformed `.sfi`/`.ddc` files, TLV parsing with truncated or unknown TLVs, RSA/ECDSA/hybrid firmware header variants, firmware download timeout and secure-send failure events, IML-to-OP two-stage boot on PCIe, ACPI PPAG/BRDS/_PRR presence and malformed package cases, EFI DSBR absent/present values, diagnostics event devcoredump creation, and shutdown LED workaround behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btintel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btintel.h -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btintel.h

## Purpose
Defines the shared Intel Bluetooth contract between common Intel support and individual transports. It centralizes TLV identifiers, hardware/image constants, version and boot structures, DDC/SAR command payloads, per-device Intel state flags, flag helpers, and exported helper prototypes with stubs for disabled configurations.

## Important APIs, Types, And Functions
- TLV constants such as `INTEL_TLV_CNVI_TOP`, `INTEL_TLV_IMAGE_TYPE`, `INTEL_TLV_MIN_FW`, `INTEL_TLV_FW_ID`, and `INTEL_TLV_OTP_BDADDR` define the fields consumed by TLV version parsing.
- Hardware/image constants define CNVi/CNVr products, hardware variant IDs, image types `BTINTEL_IMG_BOOTLOADER`, `BTINTEL_IMG_IML`, and `BTINTEL_IMG_OP`, plus firmware ID limits.
- Packed wire structs include `struct intel_tlv`, `struct intel_version`, `struct intel_version_tlv`, `struct intel_boot_params`, `struct intel_bootup`, `struct intel_secure_send_result`, `struct intel_reset`, `struct intel_debug_features`, and `struct btintel_cp_ddc_write`.
- `struct btintel_data` is the HCI private state block used by common and PCIe code. Its bitmap is manipulated by `btintel_set_flag`, `btintel_clear_flag`, `btintel_wake_up_flag`, `btintel_test_flag`, and `btintel_wait_on_flag_timeout`.
- The prototype block exposes common Intel helpers when `CONFIG_BT_INTEL` or `CONFIG_BT_INTEL_PCIE` is enabled and otherwise supplies inline error-return stubs.

## Control Flow
This header has no runtime control flow, but it shapes setup decisions across the implementation. Version parsing fills `struct intel_version_tlv`; setup uses macros such as `INTEL_HW_PLATFORM`, `INTEL_HW_VARIANT`, `INTEL_CNVX_TOP_TYPE`, and `INTEL_CNVX_TOP_STEP` to select firmware names, feature quirks, SAR/DSBR applicability, and supported products. The state-flag macros rely on `hci_get_priv(hdev)` returning a `struct btintel_data`, so transports that use these helpers must allocate compatible private storage.

## State And Persistence
Persistent runtime state represented here is the `btintel_data.flags` bitmap and optional `acpi_reset_method` callback. The flags model firmware/boot lifecycle and device quirks: bootloader mode, active download, loaded/failed firmware, boot wait, broken command credit/shutdown behavior, legacy ROM modes, ACPI reset activity, and PCIe D0 wait. Packed structs mirror controller event/command payloads and must remain layout-stable.

## Dependencies And Integration Points
The header depends on Bluetooth core types (`struct hci_dev`, `bdaddr_t`, `struct sk_buff`), firmware and regmap declarations used by prototypes, and kernel bit/wait primitives via the including C files. It is included by `btintel.c`, Intel USB/HCI transports, and `btintel_pcie.c`; the conditional stubs let non-Intel builds compile callers while preserving link-time optionality.

## Risks And Edge Cases
Function stubs must match real prototypes; the disabled `btintel_download_firmware` stub is a compatibility-sensitive area because signature drift can break builds. Packed wire structs require endian-aware access in users. The flag helpers assume correct private-data sizing and type; using them on an HCI device not allocated with `struct btintel_data` corrupts memory. Hardware ID enums must stay synchronized with firmware naming and setup switch statements in `btintel.c` and `btintel_pcie.c`.

## Test Signals
Build coverage should include `CONFIG_BT_INTEL`, `CONFIG_BT_INTEL_PCIE`, both enabled, and both disabled caller paths. Runtime signals include correct wait-bit wakeups for `INTEL_DOWNLOADING`, `INTEL_BOOTING`, and `INTEL_WAIT_FOR_D0`; TLV version structures populated from current firmware events; and no layout regressions in packed command/event payload sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btintel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btintel_pcie.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btintel_pcie.c

## Purpose
Implements the Intel Bluetooth PCIe transport driver. It binds supported Intel PCI IDs, configures PCI/MMIO/MSI-X resources, allocates coherent DMA descriptor rings and context information for firmware, moves HCI packets over Intel's PCIe packet format, coordinates firmware boot through common `btintel` helpers, handles power-state transitions, collects hardware exception dumps, and performs bounded function-level-reset recovery.

## Important APIs, Types, And Functions
- PCI driver entry points are `btintel_pcie_probe`, `btintel_pcie_remove`, `btintel_pcie_init`, and `btintel_pcie_exit`, with PM callbacks through `btintel_pcie_pm_ops`.
- HCI callbacks installed by `btintel_pcie_setup_hdev` include `btintel_pcie_send_frame`, `btintel_pcie_setup`, `btintel_shutdown_combined`, `btintel_pcie_hw_error`, `btintel_pcie_reset`, `btintel_pcie_wakeup`, `btintel_set_diag`, and `btintel_set_bdaddr`.
- DMA/ring setup is handled by `btintel_pcie_alloc`, `btintel_pcie_init_ci`, `btintel_pcie_setup_txq_bufs`, `btintel_pcie_setup_rxq_bufs`, `btintel_pcie_setup_dbgc`, and `btintel_pcie_free`.
- Interrupt and packet flow centers on `btintel_pcie_irq_msix_handler`, `btintel_pcie_msix_tx_handle`, `btintel_pcie_msix_rx_handle`, `btintel_pcie_msix_gp0_handler`, `btintel_pcie_recv_frame`, and `btintel_pcie_rx_work`.
- Recovery and diagnostics use `btintel_pcie_dump_debug_registers`, `btintel_pcie_read_hwexp`, `btintel_pcie_dump_traces`, `btintel_pcie_read_dram_buffers`, `btintel_pcie_reset_bt`, and the recovery-count list keyed by PCI BDF.

## Control Flow
Probe allocates `struct btintel_pcie_data`, initializes locks/wait queues/workqueue, enables PCI master/DMA/BAR/MSI-X, allocates descriptor memory, writes context-info DMA addresses to CSR registers, enables the Bluetooth function, pre-posts RX buffers, and registers an HCI device. HCI setup then reads TLV version data, validates supported variants, applies common Intel quirks, calls `btintel_bootloader_setup_tlv`, saves coredump header metadata, and marks setup complete. If setup fails once, it dumps registers, disables and synchronizes interrupts, performs a shared hardware reset, reinitializes index arrays/MSI-X/hardware, and retries once.

TX prepends a four-byte Intel PCIe packet type to the HCI skb, copies the packet into the current TFD DMA buffer, advances the transfer head index, rings the TX doorbell, waits for a TX completion, and for reset commands also waits for a GP0 alive interrupt. RX completions consume URBD1 completion descriptors, copy RFH-stripped packet data into skb queues, resubmit the RX buffer, and process packets in an ordered workqueue. GP0 interrupts update cached boot/image registers and drive the alive context state machine for ROM, firmware download, HCI reset, Intel reset, D0, and D3. Hardware exception interrupts schedule coredump and exception-event extraction from device memory.

## State And Persistence
The main persistent state is `struct btintel_pcie_data`: PCI/HCI handles, interrupt masks, cached boot/image registers, CNVi/CNVr IDs, alive context, wait conditions, workqueue and RX skb queue, DMA pool, descriptor rings, index arrays, context-info block, DBGC buffers, dump metadata, PM event, and state flags such as `BTINTEL_PCIE_CORE_HALTED`, `BTINTEL_PCIE_COREDUMP_INPROGRESS`, `BTINTEL_PCIE_RECOVERY_IN_PROGRESS`, and `BTINTEL_PCIE_SETUP_DONE`. A module-global recovery list stores per-BDF reset attempt counts and timestamps to limit FLR retry storms. Firmware lifecycle state is shared with `btintel.c` through `struct btintel_data` attached to the HCI device.

## Dependencies And Integration Points
Depends on the PCI core, DMA coherent allocation and DMA pools, MSI-X threaded IRQs, MMIO accessors, ordered workqueues, Bluetooth HCI core and HCI driver command interface, common Intel helpers from `btintel.c`, and optional devcoredump support. The firmware-facing ABI is defined by `btintel_pcie.h`: CSR offsets, context-info layout, TFD/URBD/FRBD descriptors, RFH header, and DBGC fragment format. The driver exposes one common HCI driver command, `HCI_DRV_OP_READ_INFO`, and advertises supported PCI IDs for Blazar/Scorpius product families.

## Risks And Edge Cases
Descriptor index management is sensitive to off-by-one and stale head/tail values; missed TX completions or GP0 alive interrupts cause command timeouts. RX path resubmits buffers even after malformed frames, so descriptor corruption can cascade if tags are wrong. Interrupt masking is manually restored after reset because hardware resets masks to all ones. Recovery is intentionally bounded but still asynchronously unregisters and re-registers the HCI device, which requires careful synchronization with workqueue, IRQ, and PCI remove paths. Hardware exception parsing trusts product-specific dump addresses and TLV lengths after signature checks. Suspend/resume handles S3 differently from freeze/hibernate; failures during D0 transition can schedule FLR and coredump concurrently.

## Test Signals
Test signals include PCI probe/remove with DMA allocation failure at each stage, MSI-X cause handling for TX, RX, GP0, GP1, and HWEXP, firmware download retry after first setup failure, HCI reset and Intel reset alive waits, RX malformed packet type/length accounting, D3-hot and D0 PM transitions including missed alive interrupt retry, freeze/hibernate FLR path, recovery retry throttling within `BTINTEL_PCIE_RESET_WINDOW_SECS`, user-triggered and firmware-assert devcoredumps, and successful re-registration after FLR recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btintel_pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btintel_pcie.h -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btintel_pcie.h

## Purpose
Defines the Intel Bluetooth PCIe hardware ABI and driver-private state used by `btintel_pcie.c`: CSR offsets and bit definitions, MSI-X cause values, power states, DMA ring sizes, context-info layout, TX/RX descriptors, RFH receive header, debug buffer metadata, dump metadata, and MMIO helper accessors.

## Important APIs, Types, And Functions
- Register definitions cover function control, hardware revision, RF ID, boot stage, IPC control/status/sleep, context-info DMA addresses, image response, mailboxes, MSI-X cause/mask/IVAR registers, debug registers, and peripheral memory access registers.
- Boot-stage and function-control bits model MAC/function init, bus-master disconnect, software reset, ROM/IML/OPFW stages, lockdown, warning, abort, halted, alive, and D3-ready status.
- Packed firmware ABI structs include `struct ctx_info`, `struct tfd`, `struct urbd0`, `struct frbd`, `struct urbd1`, and `struct rfh_hdr`.
- Driver state structs include `struct data_buf`, `struct ia`, `struct txq`, `struct rxq`, `struct btintel_pcie_dbgc`, `struct btintel_pcie_dump_header`, and `struct btintel_pcie_data`.
- Inline helpers wrap MMIO and peripheral memory operations: `btintel_pcie_rd_reg32`, `btintel_pcie_wr_reg8`, `btintel_pcie_wr_reg32`, `btintel_pcie_set_reg_bits`, `btintel_pcie_clr_reg_bits`, and `btintel_pcie_rd_dev_mem`.

## Control Flow
The header is declarative, but its structures prescribe the transport flow. Probe allocates one aligned DMA block and maps it into the fields described by `ctx_info`: index arrays, TX descriptors, RX descriptors, completion rings, doorbell vectors, MSI-X vectors, and DBGC fragment location. Runtime TX and RX update the index-array pointers in `struct ia` while the device consumes the descriptor queues defined here. Power management writes the sleep-control states declared in this header and interprets boot-stage bits to decide D0/D3/error/lockdown state.

## State And Persistence
`struct btintel_pcie_data` is the persistent per-device container. It stores hardware resource ownership, runtime synchronization primitives, cached registers, DMA resources, queue state, firmware alive context, coredump buffers, and PM state. The descriptor and context structs are persistent while the device is bound because firmware reads them by DMA address. `btintel_pcie_dump_header` persists metadata collected during setup and used later in firmware assert or user-triggered dumps.

## Dependencies And Integration Points
The header integrates with Linux PCI/MSI-X types, DMA addresses and pools, wait queues, workqueues, skb queues, Bluetooth HCI devices, and Intel common constants from `btintel.h`. The packed layouts must match the PCIe firmware contract; `btintel_pcie.c` writes the addresses into CSR registers and rings doorbells using the constants here.

## Risks And Edge Cases
Register or bit definition drift breaks hardware bring-up, interrupt routing, and PM transitions. Packed bitfields in descriptors and RFH headers are compiler-layout-sensitive but match the in-tree driver contract; changes require firmware ABI awareness. The comment spelling issues do not affect behavior, but the field semantics must remain exact because firmware treats many context fields as read-only host-provided configuration. Alignment constants and descriptor counts must match allocation and queue wrap logic in the C file.

## Test Signals
Build and runtime validation should confirm `sizeof(struct ctx_info)` and descriptor layouts expected by firmware, 128-byte alignment of the shared DMA block, correct CSR writes for context-info LSB/MSB and doorbells, valid boot-stage bit interpretation for ROM/IML/OP/D3/error states, and DBGC fragment content visible to firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btintel_pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_debugfs.c

## Purpose
Provides debugfs controls and status files for the Marvell Bluetooth driver. It exposes runtime knobs for power-save mode, power-save command trigger, host-sleep mode, host-sleep command trigger, host-sleep GPIO/gap configuration, and host-sleep configuration command trigger, plus read-only status for current power-save and host-sleep state.

## Important APIs, Types, And Functions
- `struct btmrvl_debugfs_data` stores the created `config` and `status` directory dentries.
- Write/read handlers `btmrvl_hscfgcmd_write/read`, `btmrvl_pscmd_write/read`, and `btmrvl_hscmd_write/read` bridge debugfs integer writes to fields in `priv->btmrvl_dev`.
- File-operation tables connect those handlers through `simple_open` and `default_llseek`.
- `btmrvl_debugfs_init` creates debugfs directories/files under `hdev->debugfs`.
- `btmrvl_debugfs_remove` removes both directories recursively and frees the stored debugfs data.

## Control Flow
Initialization runs after HCI registration if debugfs is enabled and `hdev->debugfs` exists. It allocates a small tracking object, creates `config` files backed directly by `btmrvl_dev` fields, and creates `status` files backed by `adapter` state fields. Writing a nonzero trigger file updates the corresponding command flag, calls `btmrvl_prepare_command`, and wakes the main service thread so the command can be sent or firmware can be woken. Removal recursively deletes the directories and frees the allocation.

## State And Persistence
Debugfs state persists for the lifetime of the registered HCI device. The files expose live `btmrvl_private` fields rather than separate cached values. Trigger fields (`pscmd`, `hscmd`, `hscfgcmd`) are consumed and cleared by `btmrvl_prepare_command`. `debugfs_data` is stored in `btmrvl_private` only when `CONFIG_DEBUG_FS` is enabled.

## Dependencies And Integration Points
Depends on Linux debugfs, simple read helpers, `kstrtol_from_user`, Bluetooth HCI debugfs root creation, and Marvell core functions from `btmrvl_main.c`. It is compiled and called only through the debugfs hooks declared in `btmrvl_drv.h`; transport code does not call it directly.

## Risks And Edge Cases
The write handlers call `btmrvl_prepare_command` synchronously before waking the thread, which can block on command wait queues from a debugfs write context. Direct debugfs mutation of mode fields has little validation beyond integer parsing and integer narrowing. If allocation fails, `priv->debugfs_data` is briefly set before the null check, but remains null because the allocation returned null. Removal assumes `hdev` still has valid drvdata and adapter state.

## Test Signals
With `CONFIG_DEBUG_FS`, verify the expected `config` and `status` files appear under the HCI device debugfs root, integer writes trigger PS/HS/HSCFG commands, nonnumeric writes return parser errors, trigger files clear after command preparation, status files reflect firmware events, and removal after HCI unregister leaves no stale debugfs entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_drv.h -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_drv.h

## Purpose
Defines shared Marvell Bluetooth driver data structures, constants, vendor command/event IDs, power-management states, firmware-dump markers, function-pointer hooks, and core function prototypes used by the Marvell SDIO transport and common driver files.

## Important APIs, Types, And Functions
- Packet and timing constants include `BTM_HEADER_LEN`, `BTM_UPLD_SIZE`, `WAIT_UNTIL_HS_STATE_CHANGED`, and `WAIT_UNTIL_CMD_RESP`.
- Firmware dump helpers are represented by `enum rdwr_status`, `struct memory_type_mapping`, and markers such as `FW_DUMP_HOST_READY`, `FW_DUMP_DONE`, and `FW_DUMP_READ_DONE`.
- Runtime containers include `struct btmrvl_thread`, `struct btmrvl_device`, `struct btmrvl_adapter`, and `struct btmrvl_private`.
- Vendor opcodes and event IDs cover module config, scan-window reporting, SCO routing, BDADDR set, auto-sleep, host-sleep config/enable, config data load, and power-state events.
- Prototypes expose interrupt, event, command, HCI registration, card add/remove, and optional debugfs functions.

## Control Flow
The header itself does not execute logic, but it defines how the common driver and transport cooperate. The transport fills hardware callbacks in `struct btmrvl_private`; the main service thread uses those callbacks to process interrupts, wake firmware, and send packets. Vendor command helpers update `btmrvl_device` flags and wait on `btmrvl_adapter` wait queues. Event processing updates `btmrvl_adapter` power-save and host-sleep fields that gate TX scheduling.

## State And Persistence
`struct btmrvl_device` persists card/HCI identity, current command trigger fields, GPIO/gap configuration, download readiness, and send-command state. `struct btmrvl_adapter` persists TX queue, interrupt count, power-save mode/state, host-sleep state, wakeup retry count, command and host-sleep wait queues, command completion flag, suspend booleans, and an aligned hardware register buffer. `struct btmrvl_private` ties these together with hardware callbacks, a spinlock, optional debugfs data, and surprise-removal state.

## Dependencies And Integration Points
Includes kernel threading, wait queue, interrupt, I/O, OF/platform, PM runtime, and Bluetooth headers. It also intentionally exposes transport-independent logic to bus-specific code such as `btmrvl_sdio.c`, while debugfs and main logic include this header to share state and prototypes.

## Risks And Edge Cases
Many fields are updated from interrupt, service-thread, command-wait, debugfs, and PM contexts, so races are controlled partly by `driver_lock` and partly by wait-queue ordering. Function pointers must be installed before the service thread can process TX or interrupts. The upload size and four-byte Marvell header limit must match firmware expectations. Debugfs direct writes and device-tree configuration both mutate `gpio_gap`, so invalid board data can affect host-sleep behavior.

## Test Signals
Compile tests should cover debugfs enabled/disabled and the SDIO transport. Runtime signals include correct initialization of wait queues and skb queue, command completion wakeups, power-save/host-sleep state transitions, surprise removal waking blocked waiters, and transport callbacks being non-null before packet transmission or interrupt processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_main.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_main.c

## Purpose
Implements the Marvell Bluetooth common HCI driver core, used by the SDIO transport. It manages interrupt wakeups, Marvell vendor event handling, synchronous vendor command submission, power-save and host-sleep control, device-tree calibration/configuration, TX queue servicing from a kernel thread, HCI device registration, and card add/remove lifecycle.

## Important APIs, Types, And Functions
- Exported lifecycle functions are `btmrvl_add_card`, `btmrvl_register_hdev`, and `btmrvl_remove_card`.
- Exported event and interrupt functions are `btmrvl_interrupt`, `btmrvl_check_evtpkt`, and `btmrvl_process_event`.
- Exported command helpers include `btmrvl_send_module_cfg_cmd`, `btmrvl_pscan_window_reporting`, `btmrvl_send_hscfg_cmd`, `btmrvl_enable_ps`, `btmrvl_enable_hs`, and `btmrvl_prepare_command`.
- HCI callbacks include `btmrvl_send_frame`, `btmrvl_flush`, `btmrvl_close`, `btmrvl_open`, `btmrvl_setup`, `btmrvl_set_bdaddr`, and `btmrvl_wakeup`.
- The main worker is `btmrvl_service_main_thread`, which serializes interrupt processing, firmware wakeup, and packet download to the bus transport.

## Control Flow
`btmrvl_add_card` allocates private and adapter state, initializes queues and wait queues, starts the service kthread, records the transport card, and marks TX download ready. The transport later calls `btmrvl_register_hdev`, which allocates/registers an HCI device and installs common callbacks. HCI setup sends module bring-up, reads device-tree wake/calibration data, routes SCO to host, enables scan-window reporting if supported, enables power save, and sends host-sleep configuration.

Outgoing HCI packets are queued by `btmrvl_send_frame` unless the adapter is suspending or suspended. The service thread sleeps until an interrupt, pending TX, or wakeup retry exists. It processes hardware interrupt status through the transport callback, wakes sleeping firmware if needed, skips TX while power-save sleep or suspend is active, and otherwise sends one queued packet with a Marvell four-byte length/type header through `hw_host_to_card`. Synchronous vendor commands are queued as `MRVL_VENDOR_PKT`, set `sendcmdflag`, wake the service thread, and wait for command completion. Incoming command-complete events wake the command wait queue and suppress vendor command responses from the normal HCI path; Marvell vendor events update PS/HS/module state and may consume the skb.

## State And Persistence
State lives in `btmrvl_private`, `btmrvl_device`, and `btmrvl_adapter`. Persistent fields include TX skb queue, power-save mode and state, host-sleep mode/state, wakeup retry count, interrupt count, command completion flag, send-command flag, GPIO/gap setting, suspend flags, hardware register buffer, service thread, wait queues, and surprise-removal flag. Device-tree calibration is downloaded during setup and not retained separately. Removal wakes command and host-sleep waiters, stops the thread, unregisters/frees HCI, frees adapter buffers, and releases private state.

## Dependencies And Integration Points
Depends on Bluetooth HCI core, Marvell SDIO transport definitions from `btmrvl_sdio.h`, SDIO device access through the transport callbacks, device-tree properties `marvell,wakeup-pin`, `marvell,wakeup-gap-ms`, and `marvell,cal-data`, kernel kthreads/wait queues/skb queues, and optional debugfs initialization/removal. It integrates with board bindings for wake/calibration data and with the HCI stack through standard open/close/flush/send/setup/set_bdaddr/wakeup callbacks.

## Risks And Edge Cases
`btmrvl_enable_ps` and `btmrvl_download_cal_data` log command failures but return zero, so setup may continue after failed PS or calibration commands. `btmrvl_send_sync_cmd` waits for command completion without directly inspecting command status beyond event side effects. The service thread processes at most one TX skb per wake cycle, so sustained throughput depends on repeated wake conditions. Power-save sleep can delay TX until firmware wake succeeds, and wakeup retry handling must avoid livelock. Surprise removal must wake all waiters to avoid blocked command or host-sleep waits. Device-tree calibration requires an exact 28-byte property.

## Test Signals
Useful coverage includes module bring-up/shutdown responses, vendor command timeout and surprise-removal wakeups, command-complete filtering for vendor OGF, PS enable/disable events, host-sleep enable success/failure/timeout, firmware wake before TX while asleep, suspend/suspending rejection in `send_frame`, malformed or unknown Marvell vendor events, BDADDR set command failure, device-tree wake and calibration properties, service-thread shutdown, and debugfs-triggered command paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_main.c -->
