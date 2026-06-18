# subset-b-004261 research

Grouped source-tree-aligned research for MEI, misc, and OCXL files in `sources/distributed-fs/ceph-client/drivers/misc`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei_dev.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/mei_dev.h

## Purpose
This header is the core private contract for the Intel MEI driver. It defines device, file-client, callback, DMA, firmware-status, power-gating, timeout, and hardware-operation abstractions shared by the ME/HECI, TXE, CSC, VSC, bus, interrupt, DMA-ring, debugfs, and userspace character-device layers.

## Important APIs, types, and functions
Key state enums are `file_state`, `mei_dev_state`, `mei_dev_pxp_mode`, `mei_dev_reset_to_pxp`, `mei_file_transaction_states`, `mei_cb_file_ops`, `mei_cl_io_mode`, `mei_pg_event`, and `mei_pg_state`. Core structures are `mei_device`, `mei_cl`, `mei_cl_cb`, `mei_cl_vtag`, `mei_me_client`, `mei_dma_data`, `mei_dma_dscr`, `mei_fw_status`, `mei_fw_version`, and `mei_dev_timeouts`. `struct mei_hw_ops` is the hardware vtable; inline wrappers such as `mei_hw_reset()`, `mei_hw_start()`, `mei_write_message()`, `mei_read_hdr()`, `mei_read_slots()`, and interrupt helpers dispatch through it. Public internal entry points include `mei_device_init()`, `mei_reset()`, `mei_start()`, `mei_restart()`, `mei_stop()`, `mei_register()`, `mei_deregister()`, IRQ handlers, DMA-ring helpers, and client-bus send/receive functions.

## Control flow and state
MEI operation is organized around `mei_device`: probe code allocates hardware-specific storage in flexible member `hw[]`, calls `mei_device_init()`, then `mei_register()` and `mei_start()`. Interrupt handlers use common read/write/completion queues while hardware-specific drivers supply readiness, reset, buffer, read, and write operations. Client file handles use `mei_cl` state, flow-control credits, wait queues, pending/completed read lists, and callback queues. Device progression is tracked by `dev_state`, `hbm_state`, power-gating events, reset counters, PXP setup state, and HBM capability bits.

## State and persistence behavior
All state is in-memory kernel state. Long-lived state includes opened client handles, ME firmware client inventory, HBM negotiated feature flags, wait queues, DMA descriptors, pending callbacks, timeout work, and client-bus device lists. There is no disk persistence; firmware state is queried through `fw_status` callbacks and rendered by `mei_fw_status_str()`.

## Dependencies and integration points
The header depends on Linux device, cdev, poll, MEI UAPI, and MEI client-bus APIs plus local `hw.h` and `hbm.h`. It is integrated by PCI drivers (`pci-me.c`, `pci-txe.c`, `pci-csc.c`), platform VSC transport, MEI bus clients, debugfs, DMA ring, HBM control, and userspace char-device layers. `kind_is_gsc()` and `kind_is_gscfi()` expose GSC/GSCFI classification for newer graphics security flows.

## Risks and test signals
Risk concentrates around lock ordering on `device_lock`, callback queue lifetime, state transitions during reset/suspend, DMA-ring bounds, HBM feature negotiation, and correct hardware vtable implementation. Test signals include successful probe/start/restart/remove on each hardware backend, sysfs firmware-status reads, client connect/disconnect, read/write flow-control stress, suspend/resume/runtime-PM cycles, reset storms capped by `MEI_MAX_CONSEC_RESET`, and debugfs visibility when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei_lb.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/mei_lb.c

## Purpose
This MEI client driver exposes Intel Late Binding firmware payload upload services to Intel graphics drivers through the Linux component framework. Late Binding delivers signed runtime configuration packages, such as fan-controller or voltage-regulator data, to authentication firmware without flashing platform firmware.

## Important APIs, types, and functions
The file defines v1 MKHI request/response structures `mei_lb_req` and `mei_lb_rsp`, v2 protocol structures `mei_lb2_header`, `mei_lb2_rsp_header`, `mei_lb2_req`, and `mei_lb2_rsp`, and GUIDs for MKHI and LB services. Main helpers are `mei_lb_push_payload_v1()`, `mei_lb_check_response_v1()`, `mei_lb_push_payload_v2()`, `mei_lb_check_response_v2()`, and `mei_lb_push_payload()`. The exported component operation is `intel_lb_component_ops.push_payload`. Probe/remove are `mei_lb_probe()` and `mei_lb_remove()`.

## Control flow and state
On MEI client probe, the driver registers a component master and matches Intel PCI requesters for `INTEL_COMPONENT_LB`. A requester calls `push_payload`, which enables the MEI client, selects protocol v2 for `MEI_GUID_LB` or v1 for MKHI, sends one request or multiple chunks, waits for firmware responses, and disables the client. V1 rejects payloads larger than the MEI MTU; v2 splits payloads into MTU-sized chunks and marks first/last flags.

## State and persistence behavior
The driver keeps no persistent private payload state. Each upload is transient and synchronous over MEI. Firmware may apply volatile configuration, while the driver only holds stack or heap request buffers and component binding state.

## Dependencies and integration points
Dependencies include `linux/mei_cl_bus.h`, `linux/component.h`, PCI helpers, UUID helpers, `mkhi.h`, and DRM Intel component headers. It integrates with i915/Xe-style graphics requesters through `drm/intel/intel_lb_mei_interface.h`, with MEI client matching through `mei_cl_device_id`, and with firmware services selected by GUID.

## Risks and test signals
Important risks are protocol mismatch, incorrect endian conversion, chunk boundary errors, MTU underflow for v2 header sizing, firmware error-code propagation, requester/component matching across PCI and auxiliary parent topologies, and leaving the MEI client enabled after failure. Test signals include v1 and v2 upload success, over-MTU v1 rejection, multi-chunk v2 first/last behavior, bad response command/status handling, component bind/unbind, and probe/remove races with graphics drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei_lb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mkhi.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/mkhi.h

## Purpose
This header defines small Management Engine Kernel Host Interface message constants and packed wire structures used by MEI code that talks to MKHI firmware groups, especially firmware capability, firmware version, and graphics/PXP setup messages.

## Important APIs, types, and functions
Constants include `MKHI_FEATURE_PTT`, firmware capability group and command IDs, generic firmware-version command IDs, graphics group `MKHI_GROUP_ID_GFX`, graphics reset/memory-ready commands, and `MKHI_GFX_MEM_READY_PXP_ALLOWED`. Wire structures are `mkhi_rule_id`, `mkhi_fwcaps`, `mkhi_msg_hdr`, `mkhi_msg`, and `mkhi_gfx_mem_ready`.

## Control flow and state
There is no executable flow. Consumers embed `mkhi_msg_hdr` at the start of firmware command packets, fill group/command/result fields, and parse flexible payloads such as `mkhi_fwcaps.data[]` or `mkhi_msg.data[]`.

## State and persistence behavior
The file defines transient packed protocol state only. Data lives in MEI request/response buffers and is not persisted by the header.

## Dependencies and integration points
It depends on `linux/types.h` and is included by MEI code that constructs MKHI messages. In this subset, `mei_lb.c` uses `mkhi_msg_hdr` and `MKHI_GROUP_ID_GFX` for Late Binding v1.

## Risks and test signals
Risk centers on ABI layout: structures are packed and endian-specific fields must match firmware expectations. Tests should validate exact packet sizes, graphics-group command IDs, result-code parsing, and interoperability with firmware responses that contain only a header on error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mkhi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pci-csc.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/pci-csc.c

## Purpose
This is a PCI MEI backend for Intel discrete graphics CSC platforms. It supports a device exposing multiple HECI blocks but intentionally binds to HECI2 at a fixed BAR offset and wires it into the common MEI ME hardware implementation.

## Important APIs, types, and functions
Key functions are `mei_csc_probe()`, `mei_csc_shutdown()`, `mei_csc_remove()`, system sleep callbacks, runtime-PM callbacks, and `mei_csc_read_fws()`. The PCI ID table uses `PCI_DEVICE_DATA(INTEL, MEI_CRI, MEI_ME_CSC_CFG)`. PM operations are grouped in `mei_csc_pm_ops`.

## Control flow and state
Probe enables the PCI device with managed helpers, maps BAR0, sets a 64-bit DMA mask, creates a MEI ME device from the CSC config, sets `read_fws_need_resume`, points `hw->mem_addr` at `registers + MEI_CSC_HECI2_OFFSET`, registers the MEI char/bus device, allocates one IRQ vector, installs the shared ME IRQ handlers, and calls `mei_start()`. Unlike `pci-me.c`, firmware handshake failure is only warned so userspace can still inspect firmware status. Remove delegates to shutdown then deregisters.

## State and persistence behavior
State is held in the `mei_device` and hardware private `mei_me_hw`. Runtime suspend marks `hw->pg_state = MEI_PG_ON`; resume marks it off and invokes the IRQ thread handler to drain queues waiting for resume. No persistent storage is used.

## Dependencies and integration points
It depends on local ME hardware code (`hw-me.h`, `hw-me-regs.h`), common MEI client/core interfaces, PCI, DMA, threaded IRQs, runtime PM, and tracing. It integrates with sysfs/char-device registration through `mei_register()` and with firmware-status reporting through the custom register-read offset.

## Risks and test signals
Risks include wrong HECI offset, reading firmware-status registers while suspended, IRQ vector cleanup ordering, continuing after failed `mei_start()`, and runtime-PM races with pending writes. Test signals include CSC PCI probe, HECI2 communication, sysfs firmware-status access after failed handshake, suspend/resume, runtime idle rejection when writes are active, and IRQ cleanup on remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pci-csc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pci-me.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/pci-me.c

## Purpose
This is the main PCI backend for Intel Management Engine Interface devices across many PCH generations. It maps PCI resources, initializes the common MEI ME hardware layer, handles IRQs, and overrides runtime PM so MEI uses ME power-gating/D0i states instead of native PCI D3.

## Important APIs, types, and functions
The large `mei_me_pci_tbl` maps PCI IDs to generation configs. Core functions are `mei_me_probe()`, `mei_me_shutdown()`, `mei_me_remove()`, `mei_me_pci_suspend()`, `mei_me_pci_resume()`, `mei_me_pm_runtime_idle()`, `mei_me_pm_runtime_suspend()`, `mei_me_pm_runtime_resume()`, `mei_me_set_pm_domain()`, `mei_me_unset_pm_domain()`, `mei_me_read_fws()`, and `mei_me_quirk_probe()`.

## Control flow and state
Probe resolves the generation config, rejects quirked invalid interfaces, enables PCI, maps BAR0, sets 64-bit coherent DMA, initializes `mei_device` with ME hardware ops, installs firmware-status config-space reader, registers MEI, enables MSI if available, requests the threaded IRQ, starts MEI, sets runtime autosuspend, stores driver data, disables direct-complete, and installs a custom PM domain. If hardware power gating is supported, it drops the runtime PM reference and allows autosuspend when D0i3 is available.

## State and persistence behavior
The driver persists only kernel runtime state: `mei_device`, ME hardware state, MSI/IRQ ownership, PM domain callbacks, and PM usage count. Runtime suspend enters ME power gating via `mei_me_pg_enter_sync()`, while resume exits via `mei_me_pg_exit_sync()`. System suspend stops MEI, disables interrupts, frees IRQ/MSI, and resume re-requests IRQ and restarts the stack.

## Dependencies and integration points
It depends on PCI, DMA, MSI, interrupt, runtime PM, MEI core, ME hardware registers, generation config, and trace hooks. It integrates with the common MEI char/bus core through `mei_register()` and with power management by replacing bus PM callbacks in `dev_pm_domain`.

## Risks and test signals
Risks include PM-domain override mistakes, reset scheduling on PG failures, MSI/shared IRQ mode differences, incomplete unwind after `mei_start()` failure, and generation-config/PCI-ID mismatches. Test signals include probe across supported PCI IDs, quirk rejection, firmware status reads, read/write traffic, system suspend/resume, runtime autosuspend/resume under load, MSI and INTx modes, and remove/shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pci-me.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pci-txe.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/pci-txe.c

## Purpose
This PCI backend supports Intel TXE MEI devices on Baytrail and Cherrytrail. TXE has a distinct hardware layer and aliveness-based runtime power model, so this file adapts PCI probe, IRQ, system sleep, and runtime PM to `hw-txe` operations.

## Important APIs, types, and functions
Important functions are `mei_txe_probe()`, `mei_txe_shutdown()`, `mei_txe_remove()`, `mei_txe_pci_suspend()`, `mei_txe_pci_resume()`, `mei_txe_pm_runtime_idle()`, `mei_txe_pm_runtime_suspend()`, `mei_txe_pm_runtime_resume()`, `mei_txe_set_pm_domain()`, and `mei_txe_unset_pm_domain()`. PCI IDs are Intel `0x0F18` and `0x2298`.

## Control flow and state
Probe maps the SEC and bridge BARs, sets a 36-bit DMA mask falling back to 32-bit, initializes `mei_txe_hw`, registers MEI, enables MSI, clears interrupts, requests MSI or shared threaded IRQ handlers, starts MEI, configures autosuspend, stores driver data, disables direct-complete, installs a PM domain, and drops the runtime reference. Runtime suspend checks write idleness and clears TXE aliveness while keeping IRQs on because the device remains in D0; runtime resume enables interrupts and sets aliveness.

## State and persistence behavior
All state is runtime kernel state inside `mei_device` and `mei_txe_hw`. System sleep tears down IRQ/MSI and restarts on resume. Runtime PM toggles device aliveness rather than PCI D-state persistence.

## Dependencies and integration points
It depends on PCI, runtime PM, threaded IRQs, and the TXE hardware layer (`hw-txe.h`). It integrates with common MEI registration and generic PM through a custom PM domain, similar to `pci-me.c` but with TXE-specific aliveness calls.

## Risks and test signals
Risks include dual-BAR mapping errors, DMA mask fallback, keeping IRQs active in runtime suspend, stale interrupts around resume, and reset scheduling after aliveness failures. Test signals include probe on Baytrail/Cherrytrail, MSI and INTx IRQ handling, `mei_start()` success, runtime autosuspend/resume with active writes rejected, system suspend/resume IRQ re-request, and clean remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pci-txe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/platform-vsc.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/platform-vsc.c

## Purpose
This platform driver adapts Intel Visual Sensing Controller transport (`vsc_tp`) into the generic MEI core by providing a `mei_hw_ops` implementation over SPI/GPIO packet transfers rather than PCI MMIO registers.

## Important APIs, types, and functions
The private hardware structure is `mei_vsc_hw`, holding the transport pointer, readiness flags, write lock count, RX header/length, and aligned TX/RX buffers. Hardware ops include `mei_vsc_hw_start()`, `mei_vsc_hw_reset()`, `mei_vsc_write()`, `mei_vsc_read()`, `mei_vsc_read_slots()`, buffer-depth helpers, interrupt wrappers, and PG stubs. Driver callbacks are `mei_vsc_probe()`, `mei_vsc_remove()`, `mei_vsc_suspend()`, `mei_vsc_resume()`, and event callback `mei_vsc_event_cb()`.

## Control flow and state
Probe receives a `struct vsc_tp *` through platform data from the SPI transport driver, allocates a MEI device plus hardware storage, initializes MEI with `mei_vsc_hw_ops`, marks firmware-version support off, sets `kind = "ivsc"`, registers the transport event callback, registers MEI, starts MEI, and enables runtime PM. Start sets `host_ready`, enables VSC interrupts, and polls a transport read until firmware responds. Interrupt/event work loops while `vsc_tp_need_read()`, dispatching common MEI read/write/completion handlers under `device_lock`.

## State and persistence behavior
State is volatile: VSC readiness booleans, cached RX packet content, TX serialization via `write_lock_cnt`, and MEI core state. Reset toggles VSC firmware through the transport and reinitializes firmware when interrupts are requested. Power gating is effectively disabled (`MEI_PG_OFF`, `pg_is_enabled=false`).

## Dependencies and integration points
It depends on platform devices, runtime PM, timekeeping for host timestamps, unaligned access, common MEI core, and `vsc-tp.h`. It integrates with the SPI VSC transport via callbacks and exported namespace `VSC_TP`; it presents the resulting controller as a normal MEI device.

## Risks and test signals
Risks include malformed RX header/length pairs, over-MTU writes, atomic write-lock imbalance, event callback races with reset/remove, firmware readiness timeouts, and mismatch between MEI slot semantics and transport packet lengths. Test signals include SPI child platform creation, firmware-ready poll success/failure, MEI message read/write, event-driven queue dispatch, suspend rejection while writes are active, remove callback unregistering, and reset plus firmware-loader path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/platform-vsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/Kconfig

## Purpose
This Kconfig entry controls the Intel MEI PXP client driver, which supplies Protected Xe Path services for Intel graphics through the ME firmware interface.

## Important APIs, types, and functions
It defines `CONFIG_INTEL_MEI_PXP` as a tristate option named "Intel PXP services of ME Interface". It depends on `INTEL_MEI_ME` and on at least one Intel graphics stack being enabled (`DRM_I915!=n` or `DRM_XE!=n`) or `COMPILE_TEST`.

## Control flow and state
There is no runtime flow. Build selection determines whether `mei_pxp.o` can be compiled and loaded.

## State and persistence behavior
No runtime state or persistence exists in this file. It influences build configuration only.

## Dependencies and integration points
The option integrates with the MEI ME transport and Intel graphics drivers. The `COMPILE_TEST` allowance lets broader build testing cover the driver without a full graphics runtime.

## Risks and test signals
Risks are incorrect dependency gating causing unresolved symbols or missing PXP support. Test signals are allmodconfig/allyesconfig builds, `COMPILE_TEST` builds, and configurations with i915 or Xe enabled as modules or built-ins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/Makefile

## Purpose
This Makefile connects the PXP MEI client driver object to the `CONFIG_INTEL_MEI_PXP` build option.

## Important APIs, types, and functions
The only build rule is `obj-$(CONFIG_INTEL_MEI_PXP) += mei_pxp.o`.

## Control flow and state
There is no runtime flow. The kernel build includes `mei_pxp.o` when the Kconfig option is enabled as built-in or module.

## State and persistence behavior
No runtime or persistent state exists.

## Dependencies and integration points
It depends on the Kbuild system and the `INTEL_MEI_PXP` Kconfig symbol. It integrates the local `mei_pxp.c` source into the MEI PXP subdirectory build.

## Risks and test signals
Risks are limited to object naming and Kconfig mismatch. Test signals include module/built-in builds and verifying that `mei_pxp.ko` is produced when configured as `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/mei_pxp.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/mei_pxp.c

## Purpose
This MEI client driver bridges Intel graphics PXP/TEE operations to ME firmware. It exposes send, receive, and GSC scatter-gather command operations to i915 through the component framework and binds to the PAVP/PXP MEI client GUID.

## Important APIs, types, and functions
Core operations are `mei_pxp_send_message()`, `mei_pxp_receive_message()`, and `mei_pxp_gsc_command()`, published through `i915_pxp_component_ops`. Recovery helper `mei_pxp_reenable()` disables and re-enables the MEI client after selected send/receive failures. Component functions are `mei_component_master_bind()`, `mei_component_master_unbind()`, and `mei_pxp_component_match()`. Driver entry points are `mei_pxp_probe()` and `mei_pxp_remove()`.

## Control flow and state
Probe enables the MEI client, allocates an `i915_pxp_component`, creates a typed component match against Intel VGA/display PCI devices and `I915_COMPONENT_PXP`, stores component data in the MEI client, and registers as component master. Bind assigns ops and `tee_dev`, then binds all matching graphics components. Send and receive are synchronous MEI client operations with caller-supplied timeouts; on `-ENOMEM`, `-ENODEV`, or `-ETIME`, the channel is reenabled. Receive retries once after `-ENOMEM` with a short sleep.

## State and persistence behavior
Persistent runtime state is limited to the allocated component structure and enabled MEI client. PXP protocol messages and GSC scatterlists are transient. Removal unregisters the component master, frees component state, clears driver data, and disables the MEI client.

## Dependencies and integration points
It depends on MEI client bus APIs, Linux component framework, PCI matching, DRM i915 component headers, and `mei_pxp.h`. It integrates with i915 PXP code and GSC command transport through `mei_cldev_send_gsc_command()`.

## Risks and test signals
Risks include component topology matching for integrated vs discrete graphics, reenable masking deeper firmware failures, receive retry behavior around unclaimed responses, lifetime of `tee_dev`, and cleanup when component registration fails after client enable. Test signals include i915 component bind/unbind, PXP session negotiation, GSC command path, timeout/error recovery, remove while bound, and configurations with Xe/i915 dependency variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/mei_pxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/mei_pxp.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/mei_pxp.h

## Purpose
This small header declares PXP status values shared by the MEI PXP client implementation.

## Important APIs, types, and functions
It defines `enum me_pxp_status`, currently containing `ME_PXP_STATUS_SUCCESS = 0x0000`.

## Control flow and state
There is no executable control flow. The enum is a protocol/status definition.

## State and persistence behavior
No state is stored. Values are intended for transient ME firmware response interpretation.

## Dependencies and integration points
The header is included by `mei_pxp.c` and guarded by `__MEI_PXP_H__`. It is part of the MEI PXP client ABI boundary inside the driver.

## Risks and test signals
Risk is low but future firmware statuses must remain ABI-compatible and correctly mapped. Test signals include compilation with the header and PXP success response handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/mei_pxp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-fw-loader.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-fw-loader.c

## Purpose
This file implements Visual Sensing Controller firmware loading over the VSC transport ROM protocol. It identifies the camera sensor and silicon stepping, selects CSI/ACE/SKU firmware blobs from `intel/vsc/`, validates image containers, downloads bootloader and firmware fragments, and boots the camera firmware.

## Important APIs, types, and functions
Important structures are `vsc_rom_cmd`, `vsc_rom_cmd_ack`, `vsc_fw_cmd`, `vsc_img`, `vsc_fw_sign`, `vsc_img_frag`, and `vsc_fw_loader`. Key helpers are `vsc_get_sensor_name()`, `vsc_identify_silicon()`, `vsc_identify_csi_image()`, `vsc_identify_ace_image()`, `vsc_identify_cfg_image()`, `vsc_download_bootloader()`, `vsc_download_firmware()`, and exported `vsc_tp_init()`. `vsc_sum_crc()` computes the protocol checksum.

## Control flow and state
`vsc_tp_init()` allocates loader and fixed-size command buffers, gets the sensor name from ACPI `SID`, queries silicon EFUSE and strap data through ROM dump commands, loads and validates the CSI image, ACE image named by sensor, and SKU config image, maps their fragments into `frags[]`, downloads the bootloader with ROM `DL_START`/`DL_CONT`, then sends firmware `DL_SET`, downloads each non-bootloader fragment in 512-byte chunks, and finally issues `CAM_BOOT`.

## State and persistence behavior
Firmware images are requested and released during initialization only. Loader state is transient heap state managed with cleanup attributes, and firmware contents are not persisted. Device firmware state changes from ROM to loaded runtime firmware after successful boot.

## Dependencies and integration points
It depends on ACPI, Linux firmware loader, unaligned access, bitfield helpers, string lowercasing, and the `vsc_tp_rom_xfer()` transport API. It is invoked by the VSC transport/MEI reset path through exported namespace `VSC_TP`.

## Risks and test signals
Risks include image bounds validation, flexible container parsing, sensor-name buffer length, protocol checksum offsets, fragment-location fallback, zero-size fragments, ROM vs firmware package size mismatch, and cleanup when one firmware request fails. Test signals include missing/invalid firmware files, ACPI SID variations, unsupported silicon stepping rejection, bootloader download chunking, firmware fragment download and boot success, and reset-triggered reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-fw-loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-tp.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-tp.c

## Purpose
This SPI driver implements the Intel VSC transport layer. It manages ACPI-described GPIOs, reset and wake handshakes, packet framing, CRC/sequence validation, IRQ-driven events, ROM transfers, and creation of a child platform device consumed by `platform-vsc.c`.

## Important APIs, types, and functions
Private types are `vsc_tp_packet_hdr`, `vsc_tp_packet`, and `vsc_tp`. Exported APIs are `vsc_tp_xfer()`, `vsc_tp_rom_xfer()`, `vsc_tp_reset()`, `vsc_tp_need_read()`, `vsc_tp_register_event_cb()`, `vsc_tp_intr_enable()`, `vsc_tp_intr_disable()`, and `vsc_tp_intr_synchronize()`. Driver callbacks include `vsc_tp_probe()`, `vsc_tp_remove()`, `vsc_tp_isr()`, and `vsc_tp_event_work()`.

## Control flow and state
Probe allocates transport and packet buffers, registers ACPI GPIO mappings, gets wakeup/reset GPIOs, initializes wait queues and locks, requests a falling-edge threaded IRQ, finds the single ACPI child, and registers platform device `intel_vsc` with the transport pointer as platform data. Normal transfer builds a sync/cmd/len/seq packet, appends CRC, wakes firmware, performs SPI transfers until a complete response is reconstructed, validates CRC and sequence, rejects ACK/NACK/BUSY command responses, and releases wake. ROM transfer uses fixed-size big-endian SPI blocks and polls GPIO readiness.

## State and persistence behavior
State is in-memory: SPI pointer, child platform device, GPIO descriptors, sequence counter, packet buffers, IRQ assertion count, event callback/context, and locks. Reset toggles firmware reset GPIO, waits for ROM boot, returns wake GPIO to inactive, and clears assertion count. No persistent storage is used.

## Dependencies and integration points
It depends on ACPI, GPIO descriptors, SPI core, IRQs, CRC32, wait queues, workqueues, and platform-device registration. It integrates upward through exported `VSC_TP` APIs and downward through ACPI IDs `INTC1009`, `INTC1058`, `INTC1094`, and `INTC10D0`.

## Risks and test signals
Risks include packet reassembly edge cases, CRC complement calculation, sequence wrap/validation, wake GPIO timing, IRQ enable/disable balance, child platform lifetime during shutdown, and callback races. Test signals include ACPI probe, GPIO acquisition, IRQ event delivery, ROM firmware download, normal read/write transfers, CRC/sequence fault rejection, reset behavior, and remove/shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-tp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-tp.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-tp.h

## Purpose
This header declares the public VSC transport API and command IDs shared by the SPI transport, firmware loader, and MEI platform adapter.

## Important APIs, types, and functions
It defines command values `VSC_TP_CMD_WRITE`, `VSC_TP_CMD_READ`, `VSC_TP_CMD_ACK`, `VSC_TP_CMD_NACK`, and `VSC_TP_CMD_BUSY`, forward-declares `struct vsc_tp`, declares callback type `vsc_tp_event_cb_t`, and prototypes ROM transfer, normal transfer, event registration, interrupt control, reset, read-needed query, and firmware init functions.

## Control flow and state
There is no implementation flow in the header. Consumers call `vsc_tp_register_event_cb()` to subscribe to transport events, `vsc_tp_xfer()` for normal framed commands, `vsc_tp_rom_xfer()` during firmware loading, and interrupt/reset helpers around MEI state transitions.

## State and persistence behavior
No state is defined beyond opaque pointer ownership and callback signatures. Actual transport state lives in `vsc-tp.c`.

## Dependencies and integration points
It depends only on `linux/types.h` and is included by `vsc-tp.c`, `vsc-fw-loader.c`, and `platform-vsc.c`. Exported functions use the `VSC_TP` namespace in implementations.

## Risks and test signals
Risks are API contract drift between the transport and platform MEI adapter, especially around callback context, IRQ-control balance, and transfer buffer lengths. Test signals are successful compilation of all VSC modules and runtime MEI-over-VSC traffic using the declared functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-tp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mrvl_cn10k_dpi.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mrvl_cn10k_dpi.c

## Purpose
This PCI misc driver controls the Marvell Octeon CN10K DPI physical function. It initializes DPI engines, exposes PF tuning ioctls, handles SR-IOV PF/VF mailbox requests, and configures per-VF DMA queue registers.

## Important APIs, types, and functions
Core data structures are `dpipf`, `dpipf_vf`, `dpivf_config`, `dpi_mbox`, and `dpi_mbox_message`. Key functions are `dpi_probe()`, `dpi_remove()`, `dpi_init()`, `dpi_fini()`, `dpi_irq_init()`, `dpi_pfvf_mbox_setup()`, `dpi_pfvf_mbox_destroy()`, `dpi_mbox_intr_handler()`, `dpi_pfvf_mbox_work()`, `queue_config()`, `dpi_queue_init()`, `dpi_queue_fini()`, `dpi_mps_mrrs_config()`, `dpi_engine_config()`, and `dpi_dev_ioctl()`.

## Control flow and state
Probe enables PCI, maps BARs, initializes global DMA/engine/EBUS registers, creates per-VF mailbox structures for up to 32 VFs, allocates a full MSI-X vector set, requests the PF/VF mailbox IRQ, enables mailbox interrupts, registers a miscdevice, and exposes simple SR-IOV configuration. When a VF mailbox interrupt arrives, the handler schedules per-VF work; work reads mailbox words, validates the VF ID, opens or closes queues, programs queue buffer/aura/PF function IDs/stream IDs, optionally sets WQE completion offset, and writes ACK/NACK.

## State and persistence behavior
Runtime state is per-PF and per-VF in memory: MMIO base, miscdevice, mailbox work/locks, VF config, and setup flags. Hardware registers hold active queue and engine configuration until reset/remove. There is no disk persistence.

## Dependencies and integration points
It depends on PCI, MSI-X, miscdevice, SR-IOV helpers, user-copy, compat ioctl, workqueues, and UAPI `uapi/misc/mrvl_cn10k_dpi.h`. It integrates with VFs through PF/VF mailbox registers and with userspace through `/dev/<module-name>` ioctls.

## Risks and test signals
Risks include mailbox trust of VF-provided fields, queue reset timeout handling, MSI-X vector count assumptions, work cancellation races, ioctl reserved-field validation, MPS/MRRS encoding, and engine FIFO/MOLR bounds. Test signals include PF probe/remove, misc ioctl validation, SR-IOV enable/disable, VF queue open/close mailbox ACK/NACK, interrupt delivery, queue reset timeout injection, and cleanup with pending mailbox work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mrvl_cn10k_dpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/nsm.c -->
# sources/distributed-fs/ceph-client/drivers/misc/nsm.c

## Purpose
This virtio driver exposes the Amazon Nitro Secure Module. It provides a raw `/dev/nsm` ioctl for CBOR request/response messages and registers an hwrng provider backed by the NSM `GetRandom` command.

## Important APIs, types, and functions
Important structures are `nsm_data_req`, `nsm_data_resp`, `nsm_msg`, and `nsm`. CBOR helpers are `cbor_object_is_array()` and `cbor_object_get_array()`. Request/response paths are `fill_req_raw()`, `parse_resp_raw()`, `nsm_sendrecv_msg_locked()`, `fill_req_get_random()`, `parse_resp_get_random()`, `nsm_rng_read()`, and `nsm_dev_ioctl()`. Virtio lifecycle functions are `nsm_device_probe()`, `nsm_device_remove()`, and `nsm_device_init_vq()`.

## Control flow and state
Probe allocates `nsm`, creates the single virtqueue, initializes the mutex, registers an hwrng named `nsm-hwrng`, then registers miscdevice `/dev/nsm` mode `0666`. Raw ioctl copies a user `nsm_raw`, copies bounded request bytes into the shared message buffer, queues one outbuf and one inbuf, kicks the virtqueue, waits up to two minutes for completion, validates returned buffers, copies/truncates the response to userspace, and returns. hwrng uses the same locked virtqueue path with a fixed CBOR `GetRandom` request and parses the random byte array from a known CBOR envelope.

## State and persistence behavior
State is volatile and serialized by `nsm->lock`: one virtqueue, one completion, one reusable message buffer, miscdevice, and hwrng registration. No persistent data is stored. Random data and raw responses are transient.

## Dependencies and integration points
It depends on virtio core, virtqueues, hwrng, miscdevice, user-copy helpers, completions, and UAPI `linux/nsm.h`. It integrates with AWS Nitro hypervisor-provided virtio device ID `VIRTIO_ID_NITRO_SEC_MOD`.

## Risks and test signals
Risks include virtqueue cleanup after partial enqueue failure, long blocking waits, raw device mode `0666`, CBOR parser limitations, response truncation semantics, mutex handling on all exits, and remove ordering (`hwrng_unregister`, `del_vqs`, `misc_deregister`). Test signals include raw ioctl success/error, oversized request rejection, timeout path, hwrng reads, malformed GetRandom response parsing, virtqueue buffer-order validation, and module remove under no-active-io conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/nsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ntsync.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ntsync.c

## Purpose
This misc driver implements Windows NT-style synchronization primitives in the kernel for userspace compatibility layers. It provides file-backed semaphore, mutex, and event objects plus wait-any and wait-all ioctls through `/dev/ntsync`.

## Important APIs, types, and functions
Core structures are `ntsync_device`, `ntsync_obj`, `ntsync_q`, and `ntsync_q_entry`. Object operations include semaphore release/read, mutex unlock/kill/read, event set/reset/pulse/read, object allocation, object file creation, and object release. Wait operations include `setup_wait()`, `ntsync_wait_any()`, `ntsync_wait_all()`, `ntsync_schedule()`, and wake helpers `try_wake_any_sem()`, `try_wake_any_mutex()`, `try_wake_any_event()`, `try_wake_all()`, and `try_wake_all_obj()`. Entry points are `ntsync_char_open()`, `ntsync_char_release()`, `ntsync_char_ioctl()`, and `ntsync_obj_ioctl()`.

## Control flow and state
Opening `/dev/ntsync` creates an isolated namespace with a device-wide `wait_all_lock`. Create ioctls return anonymous-inode fds for objects tied to that namespace. Object ioctls mutate object state and wake waiters. Wait-any queues entries on each object's `any_waiters`, checks in API order, sleeps with absolute monotonic or realtime timeout, unqueues, and returns the signaled index. Wait-all queues on each object's `all_waiters` under `wait_all_lock`, atomically locks all objects by setting `dev_locked`, consumes all signaled states together, optionally checks an alert object, then sleeps/unqueues.

## State and persistence behavior
All state is file-lifetime kernel memory. Objects hold references to the namespace file; waits hold object file references. Semaphores track count/max, mutexes track recursive count/owner/ownerdead, and events track manual-reset/signaled. No state persists after file descriptors close.

## Dependencies and integration points
It depends on anonymous inodes, miscdevice, hrtimer scheduling, signal handling, spinlocks, mutexes, user-copy, and UAPI `linux/ntsync.h`. Userspace interacts only via fds and ioctls; mode `0666` lets unprivileged processes create isolated namespaces.

## Risks and test signals
Risks include subtle lock ordering between object spinlocks and `wait_all_lock`, lost wakeups around CAS on `q->signaled`, all-wait duplicate-object rejection, ownerdead propagation, recursive mutex overflow, semaphore overflow, alert-event ordering, timeout clock semantics, and cleanup with blocked waiters. Test signals include Wine/NT primitive conformance, wait-any order, wait-all atomic consumption, manual vs auto event behavior, pulse semantics, signal interruption, timeout behavior on both clocks, object fd namespace isolation, lockdep, and stress with concurrent close/ioctl/wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ntsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/Kconfig

## Purpose
This Kconfig file controls OpenCAPI/OCXL support. It defines the base dependency symbol and the user-visible OCXL driver option for coherent accelerators exposed under `/dev/ocxl/`.

## Important APIs, types, and functions
It defines `OCXL_BASE` as a bool selecting `PPC_COPRO_BASE`, and `OCXL` as a tristate "OpenCAPI coherent accelerator support" depending on `HOTPLUG_PCI_POWERNV`, selecting `OCXL_BASE`, defaulting to module.

## Control flow and state
There is no runtime flow. Enabling `OCXL` includes the OCXL driver build and support infrastructure for PowerNV OpenCAPI devices.

## State and persistence behavior
No runtime state exists in Kconfig. It affects build-time configuration only.

## Dependencies and integration points
The option integrates with PowerPC/PowerNV PCI hotplug and coprocessor infrastructure. Help text distinguishes OCXL/OpenCAPI from IBM CAPI `CONFIG_CXL`.

## Risks and test signals
Risks are dependency drift with architecture-specific APIs and accidental build exposure on unsupported platforms. Test signals include PowerNV builds, module builds, dependency resolution for `PPC_COPRO_BASE`, and absence from unsupported platform configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/Makefile

## Purpose
This Makefile defines the OCXL composite module object list and build flags.

## Important APIs, types, and functions
`ocxl-y` includes `main.o`, `pci.o`, `config.o`, `file.o`, `pasid.o`, `mmio.o`, `link.o`, `context.o`, `afu_irq.o`, `sysfs.o`, `trace.o`, and `core.o`. `obj-$(CONFIG_OCXL) += ocxl.o` builds the module/built-in. `ccflags-$(CONFIG_PPC_WERROR) += -Werror`, and `CFLAGS_trace.o := -I$(src)` supports tracepoint include lookup.

## Control flow and state
There is no runtime flow. Build order collects OCXL subsystems into one module.

## State and persistence behavior
No runtime state exists here.

## Dependencies and integration points
It integrates with Kbuild, `CONFIG_OCXL`, PowerPC warning policy, and the tracepoint build infrastructure.

## Risks and test signals
Risks include missing object files from the composite module, trace include breakage, and Werror-only build failures. Test signals include `CONFIG_OCXL=m/y` builds and tracepoint compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/afu_irq.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/afu_irq.c

## Purpose
This file allocates, maps, handles, and frees AFU interrupt trigger pages for OCXL contexts. It bridges OpenCAPI link hardware IRQ allocation to Linux virtual IRQs and optional per-IRQ callbacks such as eventfd notification.

## Important APIs, types, and functions
The private `afu_irq` stores ID, hardware IRQ, virq, name, callback, cleanup callback, and private data. Public functions are `ocxl_irq_offset_to_id()`, `ocxl_irq_id_to_offset()`, `ocxl_irq_set_handler()`, `ocxl_afu_irq_alloc()`, `ocxl_afu_irq_free()`, `ocxl_afu_irq_free_all()`, and `ocxl_afu_irq_get_addr()`. Internal helpers are `setup_afu_irq()`, `release_afu_irq()`, `afu_irq_handler()`, and `afu_irq_free()`.

## Control flow and state
Allocation reserves an ID in the context IRQ IDR, allocates a hardware IRQ from the OCXL link, creates a Linux IRQ mapping, requests the IRQ, traces it, and returns an mmap offset. The interrupt handler dispatches the registered callback if present, otherwise drops the interrupt. Free removes the IDR entry, unmaps any userspace trigger-page mapping, frees the virq, calls private cleanup, returns the hardware IRQ to the link, and frees memory.

## State and persistence behavior
State is per-context and held in `ctx->irq_idr` under `ctx->irq_lock`. Trigger-page mappings can be invalidated through `unmap_mapping_range()` when an IRQ is freed. No persistent state exists beyond context lifetime.

## Dependencies and integration points
It depends on Linux IRQ domains, XIVE trigger-page data, PowerNV OCXL link IRQ APIs, context/AFU internal structures, and tracing. `file.c` uses it for `OCXL_IOCTL_IRQ_ALLOC`, `IRQ_FREE`, `IRQ_SET_FD`, and mmap of trigger pages.

## Risks and test signals
Risks include IDR iteration while freeing all without IDR removal, callback lifetime, trigger page address lookup, mapping invalidation, link IRQ pool exhaustion, and virq cleanup on setup failure. Test signals include IRQ allocate/free loops, eventfd handler delivery, mmap trigger pages, freeing mapped IRQs, link IRQ exhaustion, and context release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/afu_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/config.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/config.c

## Purpose
This file parses and programs OpenCAPI/OCXL PCI configuration space, especially DVSEC capabilities for functions, AFUs, transaction layer, ACTAGs, PASIDs, MMIO templates, LPC memory, reset/reload, and PASID termination.

## Important APIs, types, and functions
Public functions include `ocxl_config_read_function()`, `ocxl_config_check_afu_index()`, `ocxl_config_read_afu()`, `ocxl_config_get_reset_reload()`, `ocxl_config_set_reset_reload()`, `ocxl_config_get_actag_info()`, `ocxl_config_set_afu_actag()`, `ocxl_config_get_pasid_info()`, `ocxl_config_set_afu_pasid()`, `ocxl_config_set_afu_state()`, `ocxl_config_set_TL()`, `ocxl_config_terminate_pasid()`, and `ocxl_config_set_actag()`. Internal readers parse PASID capability, TL/function/AFU/vendor DVSECs, AFU names, template versions, MMIO, control, and memory sizes.

## Control flow and state
Function read locates required DVSECs, validates AFU/PASID consistency, logs vendor info, and records offsets. AFU read selects an AFU index in the AFU-info DVSEC, reads template fields with a valid-bit polling loop, validates names and BARs, locates AFU-control DVSEC, and extracts supported ACTAG/PASID values. Programming helpers set ACTAG/PASID bases, enable/disable AFUs, configure TL transmit/receive capabilities with platform firmware calls, and terminate PASIDs with a busy-bit timeout.

## State and persistence behavior
This code writes PCI config registers and platform TL state; changes persist in device runtime configuration until reset or driver teardown. Parsed configuration is stored in `ocxl_fn_config` and `ocxl_afu_config` held by core structures.

## Dependencies and integration points
It depends on PCI extended capabilities, OCXL config constants, PowerNV platform functions (`pnv_ocxl_*`), and internal OCXL structures. `core.c` uses it during function/AFU initialization and context detach.

## Risks and test signals
Risks include DVSEC offset assumptions, valid-bit polling timeouts, template version/length compatibility, unaligned/name parsing, total-memory shifts with large sizes, TL rate endianness, PASID termination timeout leaving unsafe state, and vendor function-0 reference handling. Test signals include devices with holes in AFU index map, missing malformed DVSECs, AFU name validation, TL setup, ACTAG/PASID programming, PASID terminate success/timeout, and reset/reload access on nonzero functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/context.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/context.c

## Purpose
This file manages OCXL per-process AFU contexts: PASID allocation, process-element attach/detach, fault-event recording, per-process MMIO and IRQ trigger-page mmap, and context cleanup.

## Important APIs, types, and functions
Public functions are `ocxl_context_alloc()`, `ocxl_context_attach()`, `ocxl_context_mmap()`, `ocxl_context_detach()`, `ocxl_context_detach_all()`, and `ocxl_context_free()`. Internal helpers include `xsl_fault_error()`, `map_pp_mmio()`, `map_afu_irq()`, `ocxl_mmap_fault()`, `check_mmap_mmio()`, and `check_mmap_afu_irq()`.

## Control flow and state
Allocation reserves a PASID from the AFU context IDR, initializes locks/wait queues/IRQ IDR, marks status `OPENED`, and takes an AFU reference. Attach transitions `OPENED` to `ATTACHED` by adding a process element on the link using current MM context, AMR, PIDR, TIDR, and fault callback. mmap validates whether the offset targets per-process MMIO or an IRQ page, sets PFNMAP/IO/noncached VMA ops, and faults insert the appropriate PFN. Detach marks the context closed, terminates the AFU PASID, removes the process element unless timeout makes it unsafe, and force-detach invalidates mappings.

## State and persistence behavior
State lives for the context fd: PASID, status, mapping pointer, xsl error record, IRQ IDR, and link process element. A detach timeout can intentionally leave the context unfreed and PASID allocated to avoid hardware checkstop risk.

## Dependencies and integration points
It depends on PowerPC MM context IDs, OCXL link APIs, config PASID termination, IRQ mapping helpers, file mapping invalidation, and internal AFU structures. `file.c` invokes it for open, attach, mmap, release, read/poll events, and ioctl operations.

## Risks and test signals
Risks include PASID leaks on detach timeout, status transitions under concurrent ioctl/release, mmap offset validation, stale mapping invalidation, fault callback races, and `ocxl_afu_irq_free_all()` cleanup. Test signals include context open/attach/release, mmap before/after attach, IRQ page mmap permission checks, xsl fault event wake/read, force detach during device removal, and PASID termination timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/core.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/core.c

## Purpose
This is the OCXL core lifecycle layer. It opens PCI functions, configures links, discovers and initializes AFUs, allocates ACTAG/PASID ranges, maps MMIO windows, activates/deactivates AFUs, and exposes metadata/accessors for other OCXL subcomponents.

## Important APIs, types, and functions
Public APIs include `ocxl_function_open()`, `ocxl_function_close()`, `ocxl_function_afu_list()`, `ocxl_function_fetch_afu()`, `ocxl_function_config()`, `ocxl_afu_config()`, `ocxl_afu_get()`, `ocxl_afu_put()`, `ocxl_afu_set_private()`, and `ocxl_afu_get_private()`. Internal helpers cover function allocation/configuration, AFU allocation/configuration/removal, ACTAG/PASID assignment/reclaim, BAR reservation, MMIO mapping, and AFU activation.

## Control flow and state
Function open requires radix MMU, allocates an `ocxl_fn`, enables PCI, reads function config, creates/registers a function device, assigns function ACTAG/PASID resources, sets up the OpenCAPI link, configures TL, then scans AFU indexes up to `max_afu_index`. Each present AFU is allocated, configured from DVSEC data, assigned ACTAG/PASID ranges, maps global/per-process MMIO, is enabled in config space, and is added to the function AFU list. Function close removes each AFU, detaches contexts, disables AFUs, releases resources, tears down link/PCI, and unregisters the function device.

## State and persistence behavior
Runtime state includes function/AFU objects, krefs, device references, AFU lists, resource bitmaps/lists, ACTAG/PASID ranges, BAR usage counts, MMIO mappings, and private AFU pointers. Hardware config persists until explicit deconfigure or reset.

## Dependencies and integration points
It depends on `config.c`, OCXL link/resource helpers, PCI, device core, IDR/list infrastructure, and internal structures. `file.c`, sysfs, and PCI frontends use AFU private pointers and metadata created here.

## Risks and test signals
Risks include resource partitioning math when enabled ACTAGs are less than supported, PASID count assumptions, BAR reference counting, MMIO ioremap failures, partial AFU init continuing after errors, device-register cleanup, and context detachment during AFU removal. Test signals include radix-disabled rejection, function open/close, AFU scan with holes, multi-AFU ACTAG/PASID allocation, BAR reuse, MMIO mapping failure unwind, and hot-unbind with active contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/file.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ocxl/file.c

## Purpose
This file provides the OCXL userspace character-device interface under `/dev/ocxl/`. It registers AFU devices, allocates minors, opens AFU contexts, dispatches ioctls, supports mmap of per-process MMIO and IRQ trigger pages, exposes event polling/reading, and cleans up contexts on release.

## Important APIs, types, and functions
Important functions are `ocxl_file_init()`, `ocxl_file_exit()`, `ocxl_file_register_afu()`, `ocxl_file_unregister_afu()`, `afu_open()`, `afu_ioctl()`, `afu_ioctl_attach()`, `afu_ioctl_get_metadata()`, `afu_ioctl_enable_p9_wait()`, `afu_ioctl_get_features()`, `afu_mmap()`, `afu_poll()`, `afu_read()`, and `afu_release()`. Device management uses `ocxl_file_info`, `minors_idr`, `ocxl_class`, `ocxl_devnode()`, and `ocxl_afu_fops`.

## Control flow and state
Module/file init reserves 256 char-device minors and registers the `ocxl` class. AFU registration allocates a minor, creates a device named from AFU name/PCI device/index, registers sysfs, adds a cdev, and stores file-info as AFU private data. Opening an AFU fd allocates an OCXL context. Ioctls attach the context, allocate/free IRQs, bind IRQs to eventfd, return metadata/features, and optionally enable POWER9 wait/TIDR support. mmap delegates to context mapping. poll/read expose XSL fault events. release detaches the context, clears mapping, wakes event waiters, and frees the context unless detach returned `-EBUSY`.

## State and persistence behavior
State is runtime only: allocated major/minors, IDR mapping, device/cdev/sysfs objects, per-open context state, eventfd IRQ handlers, and pending XSL fault records. Device nodes exist while AFUs are registered.

## Dependencies and integration points
It depends on cdev/class/device core, IDR, poll/read/ioctl/mmap file operations, eventfd, PowerPC TIDR helpers, UAPI `misc/ocxl.h`, `context.c`, `afu_irq.c`, and sysfs helpers. It is the primary userspace integration point for AFU access.

## Risks and test signals
Risks include minor IDR lifetime, device reference handling on open/unregister races, ioctl reserved-field validation, eventfd callback replacement leaks, mmap permission correctness, blocking read wakeups on close, detach timeout leaving context alive, and sysfs/cdev unregister ordering. Test signals include AFU registration/unregistration, concurrent open while unregistering, attach metadata/feature ioctls, IRQ eventfd delivery, mmap PP MMIO and IRQ pages, fault event read/poll, nonblocking read, and release during hardware errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ocxl/file.c -->
