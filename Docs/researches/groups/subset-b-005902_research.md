<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_adminq.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_adminq.h

## Purpose
Defines the AMD/Pensando PDS core AdminQ and NotifyQ wire ABI used by the core driver and auxiliary clients. The file is almost entirely command, completion, notification, queue, vDPA, live-migration, and firmware-control descriptor layout. It also exposes `pdsc_adminq_post()` as the submission helper and `pdsc_color_match()` for completion-ring ownership detection.

## Important APIs, Types, And Functions
- `enum pds_core_adminq_opcode` assigns AdminQ opcodes for client registration/proxying, LIF identify/init/reset/getattr/setattr, RX filter placeholders, queue identify/init/control, and VF get/set attributes.
- NotifyQ data is modeled by `enum pds_core_notifyq_opcode`, `struct pds_core_notifyq_event`, `struct pds_core_link_change_event`, `struct pds_core_reset_event`, `struct pds_core_client_event`, and `union pds_core_notifyq_comp`.
- Client command wrappers are `struct pds_core_client_reg_cmd`, `pds_core_client_unreg_cmd`, and `pds_core_client_request_cmd`, with `client_id` returned in `pds_core_client_reg_comp`.
- LIF and queue setup uses `union pds_core_lif_config`, `struct pds_core_lif_info`, `pds_core_lif_identity`, LIF command/completion pairs, `struct pds_core_q_identity`, `pds_core_q_identify_cmd`, and `pds_core_q_init_cmd`; `PDS_CORE_QSIZE_MIN_LG2`/`MAX_LG2` constrain ring sizes.
- vDPA support is described by `enum pds_vdpa_cmd_opcode`, `struct pds_vdpa_ident`, status/setattr/set-features commands, and virtqueue init/reset command/completion records.
- Live migration support is described by `enum pds_lm_cmd_opcode`, state-size/suspend/resume/save/restore commands, dirty-page region and bitmap commands, and host-VF status commands.
- Firmware control support is described by `enum pds_fwctl_cmd_opcode`, identify/query/RPC commands, query data records, `struct pds_sg_elem`, and RPC indirect request/response flags.
- `union pds_core_adminq_cmd` is fixed at 64 bytes and overlays all command variants; `union pds_core_adminq_comp` is fixed at 16 bytes and overlays completion variants.

## Control Flow
Callers fill one member of `union pds_core_adminq_cmd`, submit it through `pdsc_adminq_post()`, and receive a matching `union pds_core_adminq_comp`. Identify-style commands pass DMA addresses for firmware-populated side buffers. Queue/LIF init proceeds from identify to init, with queue descriptors carrying ring base DMA addresses and interrupt indexes. NotifyQ consumption uses the event code to reinterpret `union pds_core_notifyq_comp`. Completion ring processing uses the color bit, where `pdsc_color_match()` compares `PDS_COMP_COLOR_MASK` against the expected ring pass color.

## State And Persistence
Most state is device or firmware state, not kernel-owned persistence: client IDs, LIF identity/config/status, hardware queue indexes, vDPA device indexes and features, live migration state blobs, dirty tracking regions/bitmaps, and firmware-control endpoint metadata. DMA buffers handed to identify, save/restore, dirty tracking, and RPC commands persist only for the transaction unless higher layers keep them. The 64/16/64-byte static assertions are part of the ABI contract and guard persistence/layout compatibility with firmware.

## Dependencies And Integration Points
This header depends on Linux fixed-width little-endian types, bit helpers, DMA-address conventions, and status codes from the PDS core interface. It integrates with the PDS core PCI driver, auxiliary bus clients, vDPA, VFIO live migration, SR-IOV VF management, and firmware-control RPC plumbing. The final external API is `pdsc_adminq_post(struct pdsc *, union pds_core_adminq_cmd *, union pds_core_adminq_comp *, bool fast_poll)`.

## Risks And Edge Cases
Risks are ABI layout drift, endian mistakes, using the wrong union member for a completion, mismatched opcode/client/VF identifiers, DMA buffer lifetime bugs, ring-size values outside the documented log2 range, invalid scatter-gather counts, overlapping dirty-tracking regions, and incorrect completion color toggling. `PDS_CORE_ADDR_MASK`-style address limits in adjacent headers also matter for DMA addresses. `PDS_AQ_FLAG_FASTPOLL` and `fast_poll` affect polling latency, so long-running firmware operations must not be accidentally treated as short operations.

## Test Signals
Useful signals include compile-time static assertions, successful client register/unregister with stable client IDs, LIF identify/init/reset cycles, queue identify/init with valid HW queue IDs, NotifyQ link/reset/client event decoding, vDPA feature and virtqueue lifecycle tests, VFIO live-migration save/restore and dirty-bitmap tests, fwctl identify/query/RPC round trips, DMA fault injection, and completion timeout/color-wrap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_adminq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_auxbus.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_auxbus.h

## Purpose
Defines the PDS auxiliary bus device wrapper used to expose PF-managed services to auxiliary client drivers. It binds an `auxiliary_device` to the VF PCI device and the firmware-assigned PDS client ID.

## Important APIs, Types, And Functions
- `struct pds_auxiliary_dev` contains `struct auxiliary_device aux_dev`, `struct pci_dev *vf_pdev`, and `u16 client_id`.
- `pds_client_adminq_cmd()` submits a client AdminQ command on behalf of an auxiliary device, taking request/response AdminQ unions, request length, and flags.

## Control Flow
The PDS core creates or registers an auxiliary device, associates it with a VF PCI device and `client_id`, then auxiliary drivers call `pds_client_adminq_cmd()` to proxy AdminQ requests through the core. The core can wrap the request in a client command and return the firmware completion.

## State And Persistence
The persistent state in this header is the auxiliary-device identity and the assigned `client_id`. Request and response buffers are per-call transient state. Lifetime is tied to the Linux auxiliary bus device model and the parent PCI device.

## Dependencies And Integration Points
Includes `<linux/auxiliary_bus.h>` and relies on PDS AdminQ unions from the broader PDS headers. It integrates with auxiliary drivers for vDPA, VFIO/live migration, firmware control, or other PDS clients that must share the PF AdminQ path.

## Risks And Edge Cases
Risks include stale `client_id` after unregister/reset, using the helper after the auxiliary device has been removed, passing an incorrect `req_len` for a union member, and lifetime races with the VF PCI device. Error propagation from firmware status to client drivers is an important integration boundary.

## Test Signals
Exercise auxiliary-device probe/remove, client command submission, PF reset while clients are active, invalid request length handling, and client unregister paths. Successful vDPA/VFIO/fwctl auxiliary workflows are end-to-end validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_auxbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_common.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_common.h

## Purpose
Collects common PDS driver constants, device type identifiers, exported device-name strings, and public helper declarations shared between the core PDS driver and client modules.

## Important APIs, Types, And Functions
- `PDS_CORE_DRV_NAME`, `PDS_PAGE_SIZE`, `PDS_CORE_ADDR_LEN`, and `PDS_CORE_ADDR_MASK` describe common naming and address/page assumptions.
- `enum pds_core_driver_type` encodes OS/driver environments such as Linux, Windows, DPDK, FreeBSD, iPXE, ESXi.
- `enum pds_core_vif_types` classifies PDS devices as core, vDPA, VFIO, Ethernet, RDMA, live migration, and fwctl.
- `PDS_VDPA_DEV_NAME` and `PDS_VFIO_LM_DEV_NAME` build auxiliary/client names.
- Exported helpers include `pdsc_register_notify()`, `pdsc_unregister_notify()`, `pdsc_get_pf_struct()`, `pds_client_register()`, and `pds_client_unregister()`.

## Control Flow
Client drivers discover or receive the PF core object, register for notifications if needed, register a named client to get a firmware client ID, use client-specific AdminQ flows, then unregister. Notification blocks hook clients into core event distribution.

## State And Persistence
Persistent state is mostly registry state outside this header: notifier blocks, PF `struct pdsc` instances, and firmware client IDs. Constants here must stay stable because they are shared across modules and reflected in firmware-visible identify/register traffic.

## Dependencies And Integration Points
Includes `<linux/notifier.h>` and forward-declares `struct pdsc`. The prototypes integrate PDS core with PCI VFs, Linux notifier chains, auxiliary clients, vDPA, VFIO live migration, RDMA/Ethernet clients, and fwctl.

## Risks And Edge Cases
`PDS_CORE_ADDR_MASK` references `PDS_ADDR_LEN`, while this header defines `PDS_CORE_ADDR_LEN`; if no external macro supplies `PDS_ADDR_LEN`, this is a build bug. Client registration must handle duplicate names, missing PFs, reset-time unregistration, and notifier lifetime. Device type counts are bounded by `PDS_DEV_TYPE_MAX`, so firmware and driver tables must agree.

## Test Signals
Build coverage should catch the address-mask macro issue. Runtime signals include client register/unregister success, notifier callback delivery and removal, PF lookup from VF PCI device, and all named auxiliary-client probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_core_if.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_core_if.h

## Purpose
Defines the PDS core PCI device-command ABI and BAR0 register layout. This is the low-level firmware interface for device identify/init/reset, firmware download/control, SR-IOV VF management, status codes, and hardware info/command registers.

## Important APIs, Types, And Functions
- PCI and BAR constants identify Pensando/AMD devices, BAR offsets for device info, command registers, command data, interrupt status/control, and the doorbell BAR.
- `enum pds_core_cmd_opcode` defines device-command opcodes: NOP, IDENTIFY, RESET, INIT, FW_DOWNLOAD, FW_CONTROL, VF_GETATTR, VF_SETATTR, and VF_CTRL.
- `enum pds_core_status_code` maps firmware return codes such as success, invalid opcode, permission, no memory, busy, bad firmware, no client, and broken PCI status.
- `struct pds_core_drv_identity` and `struct pds_core_dev_identity` exchange driver identity and device capabilities including LIF, interrupt, doorbell, coalescing, and VIF type counts.
- Device command structures cover identify, reset, init, firmware download/control, VF attributes, and VF start control.
- `union pds_core_dev_cmd` is fixed at 64 bytes, `union pds_core_dev_comp` at 16 bytes.
- `struct pds_core_dev_info_regs`, `pds_core_dev_cmd_regs`, and `pds_core_dev_regs` describe the 4 KiB BAR0 page, including read-only device info and read/write command registers.

## Control Flow
The driver maps BAR0, verifies `PDS_CORE_DEV_INFO_SIGNATURE`, prepares `cmd_regs->cmd` and optional `cmd_regs->data`, writes the command doorbell, polls `done` for `PDS_CORE_DEV_CMD_DONE` within `PDS_CORE_DEVCMD_TIMEOUT`, then reads the typed completion. Identify and init exchange side data through the command data area. Firmware update flows download chunks by DMA address/offset/length, then issue firmware-control install/activate/status operations. VF management sends get/set/control commands with VF indexes and selected attributes.

## State And Persistence
Persistent device state includes firmware status/heartbeat/generation, serial and firmware version, hardware timestamp registers, initialized device/LIF/VF state, firmware slots, VF attributes, and active boot slot. Command register contents are transaction state. Static assertions enforce register-page sizes and ABI struct sizes.

## Dependencies And Integration Points
This header integrates the PCI core driver with firmware, SR-IOV management, firmware update tooling, interrupt setup, and the AdminQ layer that is initialized after the device-command path. It uses Linux endian types, packed layout annotations, and PCI IDs.

## Risks And Edge Cases
Key risks are BAR offset/layout drift, command register races if callers do not serialize devcmd access, timeout handling during firmware restart, endian conversion mistakes, invalid firmware slot transitions, DMA buffer/address errors during firmware download, VF attribute union misuse, and stale firmware generation after reset. The fixed data area size means identity structures must remain within the asserted 1912-byte limit.

## Test Signals
Signals include BAR signature validation, identify/init/reset on supported devices, firmware heartbeat/generation change detection, firmware download/install/activate/status tests, VF MAC/VLAN/rate/trust/spoof/link attributes, VF start-all/start flows, static assertion builds, and fault injection for timeout or `PDS_RC_BAD_PCI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_core_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_intr.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_intr.h

## Purpose
Defines PDS interrupt-control register layout, interrupt status layout, masks/credit bits, and inline MMIO helpers for coalescing, masking, rearming, and cleaning interrupts.

## Important APIs, Types, And Functions
- `struct pds_core_intr` is a 32-byte MMIO control record with `coal_init`, `mask`, signed `credits`, `flags`, `mask_on_assert`, and `coalescing_curr`.
- `PDS_CORE_INTR_F_UNMASK` and `PDS_CORE_INTR_F_TIMER_RESET` are control flags; `PDS_CORE_INTR_CTRL_REGS_MAX`, `PDS_CORE_INTR_CTRL_COAL_MAX`, and `PDS_CORE_INTR_INDEX_NOT_ASSIGNED` describe hardware limits/sentinels.
- `struct pds_core_intr_status` contains two status words.
- `enum pds_core_intr_mask_vals` defines mask clear/set values.
- `enum pds_core_intr_credits_bits` defines credit count mask, signed mask, unmask/reset/rearm bits.
- Inline helpers: `pds_core_intr_coal_init()`, `pds_core_intr_mask()`, `pds_core_intr_credits()`, `pds_core_intr_clean_flags()`, `pds_core_intr_clean()`, and `pds_core_intr_mask_assert()`.

## Control Flow
Drivers program coalescing, mask or unmask an interrupt resource, process interrupts, then write consumed credits and optional rearm flags. `pds_core_intr_credits()` protects against over-large credit counts by warning and rereading the signed credit value before writing. Cleaning reads current credits, preserves signed credit bits, ORs requested flags, and writes back to reset coalescing or rearm.

## State And Persistence
State lives in device MMIO registers. `credits` represents interrupt events sent by hardware and decremented atomically by software writes. `mask_on_assert` can cause hardware to mask after assertion, and `coalescing_curr` is hardware-managed transient timing state.

## Dependencies And Integration Points
Depends on Linux MMIO accessors `ioread32()`/`iowrite32()`, `WARN_ON_ONCE()`, and `__iomem` typing. Integrates with PDS queue completion handlers, AdminQ/NotifyQ interrupt setup, PCI interrupt allocation, and identity-provided coalescing scale factors.

## Risks And Edge Cases
Risks include treating the signed credit register as unsigned, writing a credit count above `PDS_CORE_INTR_CRED_COUNT`, failing to preserve signed bits while cleaning, using mask-on-assert in legacy interrupt mode, coalescing unit conversion mistakes, and accessing an unassigned interrupt index.

## Test Signals
Test interrupt delivery under MSI/MSI-X and legacy modes, mask/unmask behavior, coalescing timer values at 0 and max, rearm after high interrupt rates, WARN path for invalid credits, reset recovery, and queue completion progress with interrupts masked and unmasked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pe.h -->
# sources/distributed-fs/ceph-client/include/linux/pe.h

## Purpose
Provides Linux kernel definitions for PE/COFF and EFI-stub image headers. It includes Linux EFI stub version/magic constants, PE signatures, machine IDs, image flags, subsystem and DLL characteristics, section flags, debug types, executable header structs, relocation enums, and certificate structs.

## Important APIs, Types, And Functions
- `LINUX_EFISTUB_MAJOR_VERSION`, `LINUX_EFISTUB_MINOR_VERSION`, and `LINUX_PE_MAGIC` describe Linux EFI-bootable images.
- PE constants include DOS/NT signatures, optional-header magic values, machine type IDs for many architectures, image flags, subsystem IDs, DLL characteristic bits, section flags, and debug type IDs.
- Header layout structs include `struct mz_hdr`, `mz_reloc`, `pe_hdr`, `pe32_opt_hdr`, `pe32plus_opt_hdr`, `data_dirent`, `data_directory`, and `section_header`.
- Relocation enums cover x64, ARM, SH, PPC, x86, and IA64 COFF relocation types; `struct coff_reloc` overlays those enums with raw 16-bit data.
- Certificate definitions include `WIN_CERT_TYPE_*`, `WIN_CERT_REVISION_*`, and `struct win_certificate`.

## Control Flow
There is no executable control flow. Parsers or EFI-stub builders read the DOS header, follow `peaddr` to the PE header, interpret optional-header and data-directory fields, walk section headers, process relocations, and optionally inspect certificate/debug data using these definitions.

## State And Persistence
The persistent state is file-format ABI encoded in bootable images, modules, or signed PE/COFF artifacts. Struct layout must match on-disk little-endian PE fields; changing constants or field order would break image parsing and boot tooling.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and is excluded from struct definitions under `__ASSEMBLY__`. It integrates with EFI stub image creation/loading, PE/COFF parsers, secure boot/certificate handling, relocation processors, and architecture-specific boot code.

## Risks And Edge Cases
Risks include on-disk endian assumptions, PE32 versus PE32+ layout differences, alignment flag interpretation, overlapping constant values that are architecture- or OS-version-specific, flexible `message[]` sizing in `mz_hdr`, and trusting unvalidated file offsets/counts from external images.

## Test Signals
Validate EFI boot of PE32/PE32+ kernels, parse known-good Linux EFI images, check machine/subsystem/magic values, fuzz malformed headers and section counts, verify relocation decoding for supported architectures, and test secure-boot certificate table parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/peci-cpu.h -->
# sources/distributed-fs/ceph-client/include/linux/peci-cpu.h

## Purpose
Defines CPU-oriented PECI helper constants and function declarations for reading Intel CPU package telemetry, PCI configuration, endpoint PCI configuration, and MMIO over PECI.

## Important APIs, Types, And Functions
- VFM helpers copied from x86 headers encode/decode vendor-family-model values: `VFM_MODEL()`, `VFM_FAMILY()`, `VFM_VENDOR()`, and `VFM_MAKE()`.
- Includes Intel family model definitions from `../../arch/x86/include/asm/intel-family.h`.
- PECI package/config-space indexes include `PECI_PCS_PKG_ID`, package ID params, module temperature, thermal margin, DIMM temperature, temp target, and TDP units.
- Exported functions: `peci_temp_read()`, `peci_pcs_read()`, `peci_pci_local_read()`, `peci_ep_pci_local_read()`, and `peci_mmio_read()`.

## Control Flow
Consumers call the helper matching the desired PECI command. Each helper sends a request to a `struct peci_device` and fills caller-provided output such as raw temperature, package config data, PCI config dword, endpoint PCI config dword, or MMIO dword.

## State And Persistence
This header does not own state. It exposes read-only telemetry/config accessors. Persistent device identity comes from the `peci_device` and CPU vendor-family-model information.

## Dependencies And Integration Points
Depends on Linux integer types, `struct peci_device` from `peci.h`, x86 VFM conventions, and Intel family model constants. Integrates with hwmon, thermal, power, and platform-management drivers that monitor Intel CPUs through PECI.

## Risks And Edge Cases
Risks include using Intel-only VFM assumptions for non-Intel devices, invalid package config indexes/params, segment/bus/device/function/register overflow or alignment issues, PECI transport errors, and interpreting raw temperature or power-unit data without model-specific scaling.

## Test Signals
Probe PECI CPU devices, read package temperature and thermal margin, fetch CPU ID/microcode/package IDs, read local and endpoint PCI config, perform MMIO reads on valid BARs, and verify error returns for unsupported addresses or offline CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/peci-cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/peci.h -->
# sources/distributed-fs/ceph-client/include/linux/peci.h

## Purpose
Defines the Linux PECI core device model abstractions: controllers, controller operations, devices, and bounded request buffers.

## Important APIs, Types, And Functions
- `PECI_REQUEST_MAX_BUF_SIZE` caps PECI TX/RX buffers at 32 bytes.
- `struct peci_controller_ops` contains the controller-specific `xfer()` method.
- `struct peci_controller` embeds `struct device`, controller ops, a `bus_lock` mutex held for transfer duration, and a controller ID.
- `devm_peci_controller_add()` registers a managed PECI controller.
- `to_peci_controller()` and `to_peci_device()` are container helpers.
- `struct peci_device` stores device-model state, CPU identity information, PECI address, and deletion flag.
- `struct peci_request` carries the target device plus TX/RX buffers and lengths.

## Control Flow
A hardware driver registers a `peci_controller` with `devm_peci_controller_add()` and supplies `xfer()`. PECI core/device drivers build `struct peci_request` objects with TX and expected RX lengths, then the core serializes bus access with `bus_lock` and invokes the controller `xfer()` callback for a given address.

## State And Persistence
Persistent kernel state is the registered controller device, discovered PECI devices with CPU info/socket/address, and the deletion flag used during removal. Request buffers are stack or caller-owned transaction state and are bounded to 32 bytes.

## Dependencies And Integration Points
Depends on Linux device model, mutexes, kernel helpers, and fixed-width types. It integrates controller drivers on non-PECI buses, PECI CPU helper routines, hwmon/thermal/power drivers, and device lifetime management through devres.

## Risks And Edge Cases
Risks include missing bus serialization in controller drivers, buffer length overflow beyond 32 bytes, use-after-delete of `peci_device`, transfer callbacks returning partial or malformed data, and address collisions on a controller bus.

## Test Signals
Register/unregister controller drivers, enumerate PECI devices, run concurrent transfer clients to validate `bus_lock`, test max-length TX/RX requests, simulate controller errors, and remove devices while clients hold references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/peci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-defs.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu-defs.h

## Purpose
Provides the low-level declaration, definition, pointer translation, and scalar operation macros for per-CPU variables. It is intended for inclusion from architecture percpu headers and avoids cyclic dependencies with `linux/percpu.h`.

## Important APIs, Types, And Functions
- Declaration/definition macros include `DECLARE_PER_CPU_SECTION`, `DEFINE_PER_CPU_SECTION`, `DECLARE_PER_CPU`, `DEFINE_PER_CPU`, cache-hot/shared-aligned/page-aligned/read-mostly/decrypted variants, and `EXPORT_PER_CPU_SYMBOL*`.
- Pointer accessors include `per_cpu_ptr()`, `raw_cpu_ptr()`, `this_cpu_ptr()`, `per_cpu()`, `get_cpu_var()`, `put_cpu_var()`, `get_cpu_ptr()`, and `put_cpu_ptr()`.
- Type safety is enforced through `__verify_pcpu_ptr()` and `PERCPU_PTR()`.
- Size-dispatch helpers call architecture-provided 1/2/4/8-byte operations or trigger `__bad_size_call_parameter()`.
- Raw, checked, and protected operation families include `raw_cpu_read/write/add/and/or/xchg/cmpxchg/try_cmpxchg`, `__this_cpu_*`, and `this_cpu_*` plus inc/dec/sub return variants.

## Control Flow
Declarations place variables into specific per-CPU ELF sections. Accessors translate a per-CPU symbol to a CPU-specific address using `per_cpu_offset()` or arch raw CPU pointer helpers. Operation macros verify percpu pointer types, dispatch by operand size, and invoke arch-specific primitives. `get_cpu_*` disables preemption until the matching `put_cpu_*`.

## State And Persistence
Per-CPU variables are persistent kernel memory replicated per CPU or per allocation unit. Section naming and alignment control layout, locality, and cache behavior. Weak-definition logic for certain module architectures adds hidden dummy symbols to enforce scope and uniqueness.

## Dependencies And Integration Points
Depends on `CONFIG_SMP`, module settings, architecture percpu support, preemption control, relocation hiding, cacheline/page alignment macros, sparse `__percpu` typing, and arch implementations of scalar operations. It is foundational for scheduler, counters, refcounts, PMU state, and most SMP kernel code.

## Risks And Edge Cases
Risks include using `raw_cpu_*` without preemption/interrupt protection, unsupported scalar sizes, mismatched declaration/definition sections causing linkage errors, weak percpu symbol collisions, assuming `this_cpu_ptr()` is stable across preemption without protection, and architecture implementations missing required memory semantics.

## Test Signals
Build with SMP/UP, modules, debug preempt, sparse checking, and architectures with weak percpu definitions. Runtime tests should cover CPU hotplug, preemption debug warnings, per-CPU counter correctness under migration, and assembly/codegen sanity for 1/2/4/8-byte accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-refcount.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu-refcount.h

## Purpose
Defines the percpu refcount API: a scalable reference counter that uses per-CPU increments/decrements while live and switches to atomic mode for shutdown, zero detection, and release callback execution.

## Important APIs, Types, And Functions
- Mode/state bits in `percpu_count_ptr`: `__PERCPU_REF_ATOMIC`, `__PERCPU_REF_DEAD`, and `__PERCPU_REF_ATOMIC_DEAD`.
- Init flags: `PERCPU_REF_INIT_ATOMIC`, `PERCPU_REF_INIT_DEAD`, and `PERCPU_REF_ALLOW_REINIT`.
- `struct percpu_ref_data` stores atomic count, release and confirm callbacks, force/allow flags, RCU head, and backpointer.
- `struct percpu_ref` stores the tagged percpu pointer and pointer to data.
- Lifecycle APIs: `percpu_ref_init()`, `percpu_ref_exit()`, `percpu_ref_switch_to_atomic()`, `percpu_ref_switch_to_atomic_sync()`, `percpu_ref_switch_to_percpu()`, `percpu_ref_kill_and_confirm()`, `percpu_ref_kill()`, `percpu_ref_resurrect()`, `percpu_ref_reinit()`, and `percpu_ref_is_zero()`.
- Fast paths: `percpu_ref_get_many()`, `percpu_ref_get()`, `percpu_ref_tryget_many()`, `percpu_ref_tryget()`, `percpu_ref_tryget_live_rcu()`, `percpu_ref_tryget_live()`, `percpu_ref_put_many()`, `percpu_ref_put()`, and `percpu_ref_is_dying()`.

## Control Flow
Users initialize with an initial reference and a release callback. While live in percpu mode, get/put operations run inside RCU read-side sections and update per-CPU counters without checking for zero. Shutdown calls `percpu_ref_kill()` before dropping the initial reference; kill switches to atomic mode, aggregates per-CPU counts, marks dead, and then puts can detect zero and invoke release. Try-get-live can reject references after confirmed kill.

## State And Persistence
State is split between the tagged pointer in the embedded `struct percpu_ref`, allocated per-CPU counters, and `percpu_ref_data`. RCU protects switching and data lifetime. The initial reference and dead/atomic mode are part of the lifecycle protocol and must be tracked by the owner.

## Dependencies And Integration Points
Depends on atomics, percpu allocation/access, RCU, GFP allocation, and release callbacks. It integrates with high-concurrency objects such as async I/O contexts, block devices, cgroups, or kernel objects that need cheap live references and orderly two-stage teardown.

## Risks And Edge Cases
Risks include dropping the initial reference before kill, calling kill more than once without synchronization, assuming kill implies an RCU grace period, using tryget instead of tryget_live during teardown, refcount overflow beyond the documented one-bit-reduced range, force-atomic performance regressions, and use-after-exit if callers access after `percpu_ref_exit()`.

## Test Signals
Test init modes, percpu get/put under CPU migration, switch-to-atomic aggregation, kill-and-confirm ordering, release callback exactly once, resurrect/reinit paths, RCU-protected lookup patterns, CPU hotplug, and fault injection for allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-refcount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-rwsem.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu-rwsem.h

## Purpose
Defines a reader-optimized read/write semaphore where readers normally update per-CPU counters and writers use `rcu_sync` plus wait queues to block new readers and wait for existing readers to drain.

## Important APIs, Types, And Functions
- `struct percpu_rw_semaphore` contains `struct rcu_sync rss`, per-CPU `read_count`, writer `rcuwait`, waiter queue, atomic `block`, and optional lockdep map.
- Static initializers: `DEFINE_PERCPU_RWSEM()` and `DEFINE_STATIC_PERCPU_RWSEM()`.
- Reader APIs: `percpu_down_read()`, `percpu_down_read_freezable()`, `percpu_down_read_trylock()`, `percpu_up_read()`, and internal `__percpu_down_read()`.
- Writer APIs: `percpu_down_write()` and `percpu_up_write()`.
- State/lockdep helpers: `percpu_is_read_locked()`, `percpu_is_write_locked()`, `percpu_init_rwsem()`, `percpu_free_rwsem()`, `percpu_rwsem_is_write_held()`, `percpu_rwsem_is_held()`, `percpu_rwsem_assert_held()`, `percpu_rwsem_release()`, and `percpu_rwsem_acquire()`.
- Guard macros define cleanup-style read/write guards.

## Control Flow
Fast-path readers sleep-check, acquire lockdep read state, disable preemption, and increment the current CPU counter if `rcu_sync_is_idle()`. If a writer is active or pending, they enter `__percpu_down_read()`. Unlock decrements the per-CPU count and, on slow path, uses a memory barrier and wakes the blocked writer. Writers use external functions to block new readers, synchronize through `rcu_sync`, wait for per-CPU counts to drain, and release afterward.

## State And Persistence
Persistent synchronization state is the per-CPU `read_count`, `rcu_sync` state, writer wait object, wait queue, and `block` atomic. Static definitions allocate a named per-CPU counter and initialized semaphore object.

## Dependencies And Integration Points
Depends on percpu variables, RCU sync, rcuwait, wait queues, atomics, lockdep, preemption control, and cleanup guards. It is used where read-side sections are frequent and writers are rare but need global exclusion.

## Risks And Edge Cases
Risks include missing `percpu_up_read()`, sleeping in contexts where `might_sleep()` is invalid, writer starvation or missed wakeups if barriers are broken, using read locks while CPU hotplug or RCU synchronization assumptions change, and lockdep false negatives if manual acquire/release helpers are misused.

## Test Signals
Stress many readers with rare writers, trylock failure under writer pressure, freezable readers, lockdep assertions, CPU hotplug during read-heavy workloads, writer wait/wakeup correctness, and KCSAN/lockdep runs for barrier and lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-rwsem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu.h

## Purpose
Defines the generic per-CPU allocator interface, first-chunk setup data structures, allocation sizing constants, and helpers for translating per-CPU addresses.

## Important APIs, Types, And Functions
- Allocation sizing constants include `PERCPU_MODULE_RESERVE`, `PCPU_MIN_UNIT_SIZE`, `PCPU_MIN_ALLOC_SHIFT`, `PCPU_MIN_ALLOC_SIZE`, `PCPU_BITMAP_BLOCK_SIZE`, `PERCPU_DYNAMIC_SIZE_SHIFT`, `PERCPU_DYNAMIC_EARLY_SIZE`, and `PERCPU_DYNAMIC_RESERVE`.
- Global state declarations: `pcpu_base_addr`, `pcpu_unit_offsets`, `pcpu_chosen_fc`, and `pcpu_fc_names`.
- Topology/setup structures: `struct pcpu_group_info`, `struct pcpu_alloc_info`, and `enum pcpu_fc` for auto/embed/page first chunk modes.
- Boot setup APIs: `pcpu_alloc_alloc_info()`, `pcpu_free_alloc_info()`, `pcpu_setup_first_chunk()`, `pcpu_embed_first_chunk()`, optional `pcpu_populate_pte()`, `pcpu_page_first_chunk()`, and `setup_per_cpu_areas()`.
- Dynamic allocation APIs/macros: `pcpu_alloc_noprof()`, `__alloc_percpu_gfp()`, `__alloc_percpu()`, `__alloc_reserved_percpu()`, `alloc_percpu_gfp()`, `alloc_percpu()`, `alloc_percpu_noprof()`, and `free_percpu()`.
- Address helpers include `per_cpu_ptr_to_phys()`, `pcpu_nr_pages()`, `__is_kernel_percpu_address()`, and `is_kernel_percpu_address()`.

## Control Flow
Early boot builds a `pcpu_alloc_info`, chooses a first-chunk mode, lays out per-CPU units, and calls `pcpu_setup_first_chunk()`. Runtime callers allocate per-CPU objects with type-safe macros, use per-CPU accessors from lower-level headers, and release memory with `free_percpu()`. Allocation hooks wrap profiled allocation paths unless `noprof` is explicitly used.

## State And Persistence
Persistent state includes the per-CPU base address, unit offsets, first chunk, dynamic allocation metadata, reserved module/dynamic areas, and topology grouping. Allocated per-CPU objects persist until freed and have one instance per CPU/unit.

## Dependencies And Integration Points
Includes allocation tagging, memory debug, preemption, SMP, PFN helpers, init, cleanup, scheduler, and architecture percpu definitions. It integrates with slab bootstrap, module loading, CPU hotplug, NUMA-aware placement, and memory profiling.

## Risks And Edge Cases
Risks include under-sizing early dynamic reserve, unit size/alignment errors, incorrect CPU-to-node or CPU-distance callbacks, freeing invalid percpu pointers, using normal pointers for percpu memory, and first-chunk mode incompatibilities with architecture mappings or large-page assumptions.

## Test Signals
Boot on UP/SMP/NUMA, embedded and page first-chunk modes, module percpu allocations, early allocations before slab init, CPU hotplug, `is_kernel_percpu_address()` checks, allocation/free leak detection, and memory profiling/tagging coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu_counter.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu_counter.h

## Purpose
Defines a scalable approximate counter with per-CPU deltas and a global folded count on SMP, plus a simple exact scalar implementation on UP.

## Important APIs, Types, And Functions
- `PERCPU_COUNTER_LOCAL_BATCH` enables very large local batching for write-heavy/read-rare counters.
- SMP `struct percpu_counter` contains a raw spinlock, global `s64 count`, optional hotplug list node, and per-CPU `s32` counters.
- Initialization/destruction: `percpu_counter_init_many()`, `percpu_counter_init()`, `percpu_counter_destroy_many()`, and `percpu_counter_destroy()`.
- Mutation/read helpers: `percpu_counter_set()`, `percpu_counter_add_batch()`, `percpu_counter_add()`, `percpu_counter_add_local()`, `percpu_counter_sub_local()`, `percpu_counter_inc()`, `percpu_counter_dec()`, `percpu_counter_sub()`, and `percpu_counter_sync()`.
- Query helpers: `percpu_counter_read()`, `percpu_counter_read_positive()`, `percpu_counter_sum()`, `percpu_counter_sum_positive()`, `percpu_counter_compare()`, `__percpu_counter_compare()`, `percpu_counter_limited_add()`, and `percpu_counter_initialized()`.

## Control Flow
On SMP, updates add to a local per-CPU counter until a batch threshold requires folding into the global count under the raw spinlock. Reads can return the approximate global count or sum all per-CPU counters for accuracy. Compare and limited-add use batch-aware helpers. On UP, operations update the scalar count directly with IRQ protection where needed.

## State And Persistence
Persistent state is the global count plus per-CPU deltas. CPU hotplug state is tracked through a list when enabled. The count is approximate unless explicitly summed or synchronized.

## Dependencies And Integration Points
Depends on spinlocks, SMP/percpu allocation, lists, thread count, and CPU hotplug support. It integrates with filesystems and resource accounting paths that need cheap frequent updates and tolerate bounded read error.

## Risks And Edge Cases
Risks include treating `percpu_counter_read()` as exact, failing to destroy allocated per-CPU storage, negative approximate reads for logically nonnegative counters, batch values hiding limit crossings, hotplug folding races, and misuse in contexts that cannot take the internal lock.

## Test Signals
Stress concurrent increments/decrements, compare approximate versus summed values, limited-add at positive and negative limits, local batch behavior, CPU hotplug folding, UP and SMP builds, init-many/destroy-many arrays, and leak detection for allocated counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu_counter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/arm_pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/perf/arm_pmu.h

## Purpose
Defines the generic ARM PMU driver interface used by ARM and arm64 PMU implementations to integrate hardware counters with the Linux perf core.

## Important APIs, Types, And Functions
- `ARMPMU_MAX_HWEVENTS` is 32 on 32-bit ARM and 33 on arm64 to account for newer PMUv3 counters.
- ARM PMU event flags include `ARMPMU_EVT_64BIT`, `ARMPMU_EVT_47BIT`, and `ARMPMU_EVT_63BIT`, asserted to fit within `PERF_EVENT_FLAG_ARCH`.
- Mapping helpers include unsupported sentinel constants and `PERF_MAP_ALL_UNSUPPORTED`/`PERF_CACHE_MAP_ALL_UNSUPPORTED`.
- `struct pmu_hw_events` tracks active events, used counter bitmap, per-CPU PMU device ID, IRQ, branch stack, and branch-user count.
- `struct arm_pmu` embeds `struct pmu` and supplies callbacks for IRQ handling, enable/disable, event index allocation, filters, counter read/write, start/stop/reset, event mapping, PMUv3 mapping, plus CPU masks, platform device, per-CPU event state, CPU PM notifier, sysfs attr groups, PMUv3 metadata, and ACPI CPU ID.
- Public helpers include `armpmu_event_update()`, `armpmu_event_set_period()`, `armpmu_map_event()`, `arm_pmu_device_probe()`, `arm_pmu_acpi_probe()`, `kvm_host_pmu_init()`, `arm_pmu_irq_is_nmi()`, `armpmu_alloc()`, `armpmu_free()`, `armpmu_register()`, `armpmu_request_irq()`, and `armpmu_free_irq()`.
- PMU format macros generate sysfs format attributes and extract config fields.

## Control Flow
Platform or ACPI probe matches CPU/PMU information through `pmu_probe_info`, allocates `struct arm_pmu`, initializes callbacks and event maps, requests interrupts, and registers the PMU with perf. Perf core calls PMU callbacks to map events, allocate counters, program periods, start/stop counters, handle overflow IRQ/NMI, and update counts. Branch sampling and KVM host PMU setup attach through optional fields/callbacks.

## State And Persistence
State is split between the PMU object, supported CPU mask, per-CPU `pmu_hw_events`, active-event arrays, used counter bitmaps, PMUv3 capability bitmaps, IRQ assignments, and sysfs attribute groups. Counter values themselves live in hardware and are synchronized into perf event state.

## Dependencies And Integration Points
Depends on interrupts, perf core, platform devices, sysfs, CPU type detection, ACPI, KVM, and architecture PMU register implementations. It integrates with `/sys/devices/*/events` and `format` attributes, perf event scheduling, CPU PM notifications, and virtualization support.

## Risks And Edge Cases
Risks include wrong event mapping tables, counter width flag mismatch, unsupported cache events being exposed, counter index allocation races, per-CPU IRQ lifetime errors, heterogeneous CPU filtering mistakes, NMI versus IRQ handler assumptions, and PMUv3 common-event bitmap drift.

## Test Signals
Probe PMU via DT and ACPI, run `perf stat` hardware/cache events, sample overflow interrupts, validate sysfs events/format/caps, CPU hotplug and suspend/resume, branch-stack sampling, KVM host PMU initialization, heterogeneous CPU event filtering, and counter-width rollover tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/arm_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/arm_pmuv3.h -->
# sources/distributed-fs/ceph-client/include/linux/perf/arm_pmuv3.h

## Purpose
Defines ARM PMUv3 architectural event numbers, implementation-defined event numbers, register bit masks, event filter bits, user-access bits, PMMIR fields, and PMEVN switch helpers used by ARM PMUv3 drivers.

## Important APIs, Types, And Functions
- Counter indexes include `ARMV8_PMU_MAX_GENERAL_COUNTERS`, `ARMV8_PMU_CYCLE_IDX`, and `ARMV8_PMU_INSTR_IDX`.
- Architectural event constants cover software increment, cache/TLB refills and accesses, retired/speculative operations, branches, stalls, bus cycles, chain events, SPE/AMU/TRBE/trace/MTE extensions, and recommended implementation-defined events.
- PMCR masks include enable/reset/divider/export/debug/long-counter fields and `ARMV8_PMU_PMCR_MASK`.
- Overflow status masks include `ARMV8_PMU_OVSR_P`, `ARMV8_PMU_OVSR_C`, `ARMV8_PMU_OVSR_F`, and `ARMV8_PMU_OVERFLOWED_MASK`.
- Event type masks include `ARMV8_PMU_EVTYPE_EVENT`, `ARMV8_PMU_EVTYPE_TH`, and `ARMV8_PMU_EVTYPE_TC`.
- Filter bits include EL0/EL1/EL2/EL3 and secure/non-secure include/exclude controls.
- User enable bits include `ARMV8_PMU_USERENR_*` and `ARMV8_PMU_USERENR_MASK`.
- `PMEVN_SWITCH()` expands a runtime counter index into compile-time cases for PMEV0 through PMEV30 operations before including `<asm/arm_pmuv3.h>`.

## Control Flow
PMUv3 drivers map perf events to event numbers from this header, program PMXEVTYPER fields, configure PMCR/user/filter bits, check overflow status, and use `PMEVN_SWITCH()` to access per-counter registers through architecture macros. There is no runtime code in this header beyond generated switch macros.

## State And Persistence
State is hardware PMU register state: enabled counters, selected event codes, overflow flags, privilege filters, user access state, PMMIR capabilities, and current counter values. Constants must match the ARM architecture because perf event encodings and sysfs names depend on them.

## Dependencies And Integration Points
Integrates with ARM/arm64 PMU drivers, KVM PMU emulation, perf event maps, trace/SPE/TRBE code, and architecture-specific register accessors in `asm/arm_pmuv3.h`.

## Risks And Edge Cases
Risks include exposing event constants unsupported by a given PMU revision, mishandling arm64-only high bits on 32-bit ARM, off-by-one counter indexes, missing overflow bit 32 on arm64, invalid `PMEVN_SWITCH()` indexes, and privilege filter combinations that leak or hide events.

## Test Signals
Validate event maps for common architectural events, overflow handling for cycle and event counters, user access enable/disable, privilege filtering, 64-bit/long-counter behavior, PMEVN index warnings, PMUv3 revision-specific capability exposure, and KVM guest PMU event compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/arm_pmuv3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/riscv_pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/perf/riscv_pmu.h

## Purpose
Defines the RISC-V PMU integration interface for Linux perf, including per-CPU hardware event tracking, PMU callbacks, counter helpers, and SBI/legacy platform names.

## Important APIs, Types, And Functions
- Constants include `RISCV_MAX_COUNTERS`, `RISCV_OP_UNSUPP`, `RISCV_PMU_SBI_PDEV_NAME`, `RISCV_PMU_LEGACY_PDEV_NAME`, `RISCV_PMU_STOP_FLAG_RESET`, and `RISCV_PMU_CONFIG1_GUEST_EVENTS`.
- `struct cpu_hw_events` tracks enabled event count, overflow IRQ, active perf events, used hardware and firmware counter bitmaps, optional SBI snapshot virtual/physical addresses, setup flag, and shadow counter values.
- `struct riscv_pmu` embeds `struct pmu`, name, IRQ handler, counter mask, callbacks for counter read/index/width/start/stop/clear, event map/init/mapped/unmapped, CSR index, per-CPU hardware events, hlist node, and PM notifier.
- Public helpers include `riscv_pmu_start()`, `riscv_pmu_stop()`, `riscv_pmu_ctr_read_csr()`, `riscv_pmu_event_set_period()`, `riscv_pmu_ctr_get_width_mask()`, `riscv_pmu_event_update()`, `riscv_pmu_legacy_skip_init()`, `riscv_pmu_alloc()`, `riscv_pmu_get_hpm_info()`, and `riscv_pmu_get_event_info()`.

## Control Flow
RISC-V PMU drivers allocate and register a `riscv_pmu`, map perf events to hardware or firmware counters, allocate a counter index, program initial values, start/stop counters, handle overflow IRQs, and update perf counts. SBI-backed PMUs may query hardware counter width/count and event encodings and may use snapshot memory to avoid clobbering during SBI calls.

## State And Persistence
State includes the PMU object, counter mask, per-CPU `cpu_hw_events`, used-counter bitmaps, snapshot buffer address/physical address, shadow counter values, and PM notifier state. Counter values persist in CSRs or firmware-managed counters while events are active.

## Dependencies And Integration Points
Depends on perf core, ptrace, interrupts, RISC-V CSR access, optional legacy PMU and SBI PMU support, physical-address handling, and PM notifications. It integrates with platform devices named for SBI or legacy PMUs and with guest-event filtering through config1.

## Risks And Edge Cases
Risks include counter width masking errors, overlapping hardware/firmware counter allocation, SBI snapshot setup races, IRQ routing failures, unsupported operation handling, guest event exposure mistakes, legacy/SBI double initialization, and event map callbacks returning encodings unsupported by firmware.

## Test Signals
Run `perf stat` and sampling on legacy and SBI PMUs, validate counter rollover based on width, CPU hotplug and suspend/resume, overflow IRQ delivery, SBI hpm/event info queries, snapshot setup/teardown, guest event filters, and unsupported event rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/riscv_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_event.h -->
# sources/distributed-fs/ceph-client/include/linux/perf_event.h

## Purpose
Defines the kernel-internal perf event API, PMU driver interface, event/context state, sample construction helpers, software-event hooks, callchain APIs, guest perf callbacks, cgroup perf data, sysfs attribute helpers, and disabled stubs for builds without `CONFIG_PERF_EVENTS`.

## Important APIs, Types, And Functions
- Sample/raw/branch data types include `struct perf_callchain_entry`, `perf_callchain_entry_ctx`, `perf_raw_frag`, `perf_raw_record`, and `perf_branch_stack`.
- `struct hw_perf_event` stores PMU-specific hardware, AUX, software, tracepoint, breakpoint, AMD/IOMMU, sampling-period, throttling, and frequency state.
- `struct pmu` is the central PMU driver callback table: `event_init`, `add`, `del`, `start`, `stop`, `read`, transaction callbacks, `event_idx`, scheduler hooks, AUX setup/free/snapshot, address-filter validation/sync, aux-output match, CPU filter, and period check.
- Event state/capability definitions include `enum perf_event_state`, `PERF_EF_*`, `PERF_HES_*`, `PERF_PMU_CAP_*`, `enum perf_pmu_scope`, and `PERF_EV_CAP_*`.
- `struct perf_event` stores list/tree membership, group state, PMU pointers, state, attach state, counts, timings, attributes, hardware state, contexts, refs, child/owner/mmap/ring-buffer/poll/pending work/filter/AUX/BPF/security/cgroup fields.
- Context types include `struct perf_event_pmu_context`, `perf_event_groups`, `perf_time_ctx`, `perf_event_context`, `perf_ctx_data`, `perf_cpu_pmu_context`, `perf_cpu_context`, and `perf_cgroup`.
- Public APIs cover PMU registration, task sched-in/out/init/exit/free hooks, kernel counter creation, context migration, local/read-value helpers, callchains, sample preparation/output, perf output buffers, software events, BPF/ksymbol/text-poke events, mmap/fork/comm/exec/namespaces hooks, security checks, address-filter sync, AUX output, enable/disable/period/pause, CPU hotplug, and sysfs event/format attributes.
- Inline helpers build sample data (`perf_sample_data_init()`, `perf_sample_save_callchain()`, `perf_sample_save_raw_data()`, `perf_sample_save_brstack()`), test branch-sample flags, determine software/exclusive/AUX/address-filter properties, and perform scheduler software-event hooks.

## Control Flow
Userspace or kernel code creates events through perf APIs, which choose a PMU and call `pmu->event_init()`. Events attach to task or CPU contexts, join groups, and are scheduled by context switch, CPU hotplug, cgroup, or explicit enable/disable logic. PMU callbacks add/start/read/stop/del hardware state. Overflow handlers construct `perf_sample_data`, optionally save callchains/raw/branch/AUX data, and output records to ring buffers. Software events use static keys to avoid overhead when disabled. Task scheduling hooks emit context-switch/migration/cgroup events and call PMU scheduler callbacks. Disabled builds replace most APIs with stubs returning no-op or `-EINVAL`.

## State And Persistence
Perf maintains persistent PMU registrations, per-task and per-CPU contexts, event groups, refcounted events, ring buffers, mmap state, pending IRQ/task work, address filters, BPF attachments, cgroup time accounting, callchain buffers, sysctl limits, static keys, and optional guest callback static calls. Hardware counter state persists in PMU registers while active and is synchronized into `local64_t count`, time-enabled, and time-running fields.

## Dependencies And Integration Points
The header ties together UAPI perf definitions, BPF perf events, architecture perf/event and local64 support, hardware breakpoints, lists, RCU, spinlocks, hrtimers, files, pid namespaces, workqueues, ftrace, CPU hotplug, irq_work, static keys/calls, atomics, sysfs, cgroups, refcounts, security hooks, lockdep, local counters, guest/KVM callbacks, and PMU-specific architecture drivers such as ARM and RISC-V.

## Risks And Edge Cases
Risks include incorrect PMU callback locking or IRQ/NMI assumptions, group transaction rollback bugs, event state transition errors, refcount/RCU lifetime mistakes, ring-buffer overflow/lost-sample accounting, raw fragment padding errors, sample size miscalculation, branch-stack truncation, cgroup/task context races, filter generation mismatches, AUX pause/resume concurrency, security/paranoid bypasses, and inconsistent disabled-stub behavior.

## Test Signals
Use perf selftests, `perf stat`, `perf record`, sampling overflow, grouped pinned/flexible events, CPU and task events, cgroup events, BPF perf events, tracepoints, hardware breakpoints, AUX tracing, address filters, callchains, branch stacks, CPU hotplug, task fork/exec/exit, mmap output, permission/paranoid checks, PMU unregister/revoke, and `CONFIG_PERF_EVENTS=n` build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_event_api.h -->
# sources/distributed-fs/ceph-client/include/linux/perf_event_api.h

## Purpose
Acts as a compatibility/include shim that simply includes `<linux/perf_event.h>`.

## Important APIs, Types, And Functions
- No new types or functions are defined.
- Re-exports the full kernel perf event interface by including `linux/perf_event.h`.

## Control Flow
There is no control flow. Inclusion of this header causes the compiler to parse the perf event API declarations and inline helpers from `perf_event.h`.

## State And Persistence
No independent state is introduced. All state comes from the included perf event core header.

## Dependencies And Integration Points
The integration point is source compatibility for code that includes `linux/perf_event_api.h` instead of `linux/perf_event.h`.

## Risks And Edge Cases
Risk is limited to include-order or dependency churn if `perf_event.h` changes. Any consumer expecting a smaller or different API surface still receives the entire perf event header.

## Test Signals
Build coverage of consumers that include this shim is sufficient. Changes should preserve that include path and verify no circular include or missing dependency appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_event_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/perf_regs.h

## Purpose
Defines the generic perf register capture wrapper and architecture hooks used to validate, read, and expose sampled register values to perf.

## Important APIs, Types, And Functions
- `struct perf_regs` stores `struct pt_regs *regs` and a register ABI selector.
- When `CONFIG_HAVE_PERF_REGS` is enabled, architecture `<asm/perf_regs.h>` supplies `PERF_REG_EXTENDED_MASK` and implementations for `perf_reg_value()`, `perf_reg_validate()`, `perf_reg_abi()`, and `perf_get_regs_user()`.
- Without register support, inline stubs return zero or `-EINVAL` and clear `regs_user->regs`.

## Control Flow
Perf sampling code asks the architecture to validate a user-requested register mask, determine the ABI for a task, extract register values from `pt_regs`, and populate user register snapshots. In unsupported builds, validation fails and register capture is disabled.

## State And Persistence
The only state is the transient `perf_regs` view used while constructing samples. It references `pt_regs` owned by interrupt, exception, or task stack contexts and does not persist register storage itself.

## Dependencies And Integration Points
Includes task stack helpers and optional architecture perf register definitions. Integrates with perf sample types `PERF_SAMPLE_REGS_USER` and `PERF_SAMPLE_REGS_INTR`, callchain capture, and BPF perf event register views.

## Risks And Edge Cases
Risks include stale `pt_regs` pointers, exposing registers with the wrong ABI, accepting unsupported masks, architecture stubs hiding missing support, and user-register capture from tasks without a valid saved user register frame.

## Test Signals
Run perf register sampling on supported architectures, validate bad masks return `-EINVAL`, test 32-bit compatibility tasks on 64-bit kernels, sample interrupt and user registers, and build unsupported architectures to confirm clean stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/personality.h -->
# sources/distributed-fs/ceph-client/include/linux/personality.h

## Purpose
Provides kernel-side wrappers around UAPI process personality constants and simple helpers for reading and setting the current task personality.

## Important APIs, Types, And Functions
- Includes `<uapi/linux/personality.h>` for personality flags and masks.
- `personality(pers)` masks a personality value with `PER_MASK`.
- `get_personality` aliases `current->personality`.
- `set_personality(pers)` writes `current->personality`.

## Control Flow
Callers read the current task personality through `get_personality`, mask personality domains with `personality()`, or set the current task value with `set_personality()`. There are no functions or validation paths in this header.

## State And Persistence
State is the `personality` field in `current`/`task_struct`, which persists for the task and influences execution-domain behavior, ABI quirks, address layout, and related process semantics.

## Dependencies And Integration Points
Depends on UAPI personality definitions and the implicit `current` task pointer. It integrates with exec, binfmt loaders, compatibility modes, address-space randomization policy, and process-control syscalls.

## Risks And Edge Cases
Risks include setting personality flags without preserving required bits, failing to mask with `PER_MASK` when comparing domains, and changing `current->personality` in contexts where another task was intended.

## Test Signals
Exercise `personality(2)`, exec of compatibility binaries, ASLR/personality flag interactions, domain masking, and build coverage where `current` is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/personality.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pfn.h -->
# sources/distributed-fs/ceph-client/include/linux/pfn.h

## Purpose
Defines basic PFN/physical-address conversion and page-alignment macros.

## Important APIs, Types, And Functions
- `PFN_ALIGN(x)` rounds an address-like value up to a page boundary.
- `PFN_UP(x)` converts bytes/addresses to a page count rounded up.
- `PFN_DOWN(x)` converts bytes/addresses to a page frame number rounded down.
- `PFN_PHYS(x)` converts a PFN to `phys_addr_t`.
- `PHYS_PFN(x)` converts a physical address to an unsigned long PFN.

## Control Flow
There is no runtime control flow. These macros expand into shifts and masks using `PAGE_SIZE`, `PAGE_SHIFT`, and `PAGE_MASK`.

## State And Persistence
No state is stored. The macros are pure arithmetic but depend on architecture page-size constants and `phys_addr_t` width.

## Dependencies And Integration Points
Includes `<linux/types.h>` and integrates broadly with memory management, bootmem, device memory, page tables, DMA, and per-CPU allocator sizing.

## Risks And Edge Cases
Risks include overflow when aligning large values, truncation in `PHYS_PFN()` to unsigned long on platforms with wider physical addresses, using macros with signed values, and assuming page size is 4 KiB.

## Test Signals
Build across page sizes and physical-address widths, verify boundary conversions around page edges, test large physical addresses, and use sparse/compiler warnings to catch type truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgalloc.h -->
# sources/distributed-fs/ceph-client/include/linux/pgalloc.h

## Purpose
Provides generic page-table allocation include glue and fallback population macros for kernel page-table levels.

## Important APIs, Types, And Functions
- Includes `<linux/pgtable.h>` and architecture `<asm/pgalloc.h>`.
- `pgd_populate_kernel(addr, pgd, p4d)` defaults to `pgd_populate(&init_mm, pgd, p4d)` when the architecture does not define it.
- `p4d_populate_kernel(addr, p4d, pud)` defaults to `p4d_populate(&init_mm, p4d, pud)` when not defined.

## Control Flow
Architecture or generic MM code includes this header and calls the kernel population helpers while constructing kernel page tables. The fallback helpers route through `init_mm`; architectures can override them when address-aware population is needed.

## State And Persistence
State is page-table hierarchy state in kernel memory, typically under `init_mm` for kernel mappings. This header introduces no independent storage.

## Dependencies And Integration Points
Integrates generic memory-management code with architecture page-table allocators and page-table population routines. It depends on `init_mm`, `pgd_populate()`, and `p4d_populate()` being available from included MM headers.

## Risks And Edge Cases
Risks include using fallback helpers on architectures that require address-specific handling, incorrect page-table level folding assumptions, and modifying kernel mappings without proper synchronization/TLB maintenance in callers.

## Test Signals
Build architectures with and without custom `*_populate_kernel`, boot with folded and non-folded page-table levels, exercise vmalloc/ioremap/kernel mapping setup, and run page-table debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgalloc_tag.h -->
# sources/distributed-fs/ceph-client/include/linux/pgalloc_tag.h

## Purpose
Defines page-allocation tagging helpers used by memory allocation profiling to associate pages with allocation codetags, including compact page-extension references, module/kernel tag index conversion, and folio tag maintenance.

## Important APIs, Types, And Functions
- Under `CONFIG_MEM_ALLOC_PROFILING`, externs include `page_alloc_tagging_ops`, `alloc_tag_ref_mask`, `alloc_tag_ref_offs`, `kernel_tags`, and optional `module_tags`.
- `typedef u16 pgalloc_tag_idx` stores compact tag indexes. `union pgtag_ref_handle` carries a page extension and flags.
- Tag index constants are `CODETAG_ID_NULL`, `CODETAG_ID_EMPTY`, and `CODETAG_ID_FIRST`.
- Module/kernel conversion helpers include `module_idx_to_tag()`, `module_tag_to_idx()`, `idx_to_ref()`, and `ref_to_idx()`.
- Page reference helpers include `get_page_tag_ref()`, `put_page_tag_ref()`, `update_page_tag_ref()`, `__clear_page_tag_ref()`, `clear_page_tag_ref()`, `__pgalloc_tag_get()`, and `pgalloc_tag_get()`.
- Folio/lifecycle hooks include `pgalloc_tag_split()`, `pgalloc_tag_swap()`, and `alloc_tag_sec_init()`.
- Without `CONFIG_MEM_ALLOC_PROFILING`, all public helpers are no-op or return `NULL`.

## Control Flow
When profiling is enabled, page allocation paths acquire a page-extension codetag reference, encode or decode the allocation tag index, update the page reference, and release the handle. Clearing removes the tag reference from a page. Folio split/swap paths preserve or move tag accounting. Initialization sets up kernel and module tag sections. Disabled builds compile away the work.

## State And Persistence
Persistent profiling state lives in page extension records and allocation tag sections for kernel and modules. A page can carry a compact reference to the codetag that allocated it. Module tag indexes are offset from the kernel tag section and must remain valid while module tags exist.

## Dependencies And Integration Points
Depends on allocation tagging, page extensions, module support, folio/page types, and memory allocation profiling configuration. Integrates with page allocator instrumentation, module codetag sections, folio splitting/swapping, and allocation-profile reporting.

## Risks And Edge Cases
Risks include stale module tag references after module unload, index overflow in 16-bit `pgalloc_tag_idx`, incorrect kernel/module offset conversion, racing page-extension updates, leaked references if `put_page_tag_ref()` is missed, and losing tags across folio split/swap. Disabled stubs can hide missing profiling coverage in tests.

## Test Signals
Build with and without `CONFIG_MEM_ALLOC_PROFILING` and `CONFIG_MODULES`, allocate/free tagged pages, load/unload modules with allocation tags, split and swap folios, clear page tags, run page-extension debug checks, and verify reports attribute page allocations to expected codetags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgalloc_tag.h -->
