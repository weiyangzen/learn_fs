# Research: subset-b-005585

This grouped report covers the requested `drivers/virt` source subset under `sources/distributed-fs/ceph-client`. Each file section is bounded with the required markers for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/ioreq.c -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/ioreq.c

## Purpose
Implements ACRN Hypervisor Service Module I/O-request dispatch. It pins the shared I/O request page supplied by userspace, registers an ACRN interrupt handler, walks every live VM for pending hypervisor requests, converts special PCI config-port traffic, and routes work either to the default userspace client or to kernel ioreq clients such as ioeventfd.

## APIs, Types, and Functions
Important exported helpers are `acrn_ioreq_init()`, `acrn_ioreq_deinit()`, `acrn_ioreq_intr_setup()`, `acrn_ioreq_intr_remove()`, `acrn_ioreq_client_create()`, `acrn_ioreq_client_destroy()`, `acrn_ioreq_range_add()`, `acrn_ioreq_range_del()`, `acrn_ioreq_client_wait()`, `acrn_ioreq_request_clear()`, and `acrn_ioreq_request_default_complete()`. Internal control centers include `ioreq_dispatcher()`, `acrn_ioreq_dispatch()`, `find_ioreq_client()`, `ioreq_task()`, and `handle_cf8cfc()`. It depends on `struct acrn_vm`, `struct acrn_ioreq_client`, and `struct acrn_io_request` from the ACRN HSM headers and hypercall ABI.

## Control Flow and State
`acrn_ioreq_intr_setup()` registers `ioreq_intr_handler()` and creates a high-priority ordered workqueue. Interrupts queue `ioreq_work`; `ioreq_dispatcher()` takes `acrn_vm_list_lock`, scans VMs, and calls `acrn_ioreq_dispatch()` for each VM with an `ioreq_buf`. Dispatch uses acquire/release barriers around `req->processed`, handles CF8/CFC PCI config pairing in-place, finds a matching client by protected range lists, marks kernel-vs-userspace ownership with `kernel_handled`, sets the processing state, records the vCPU bit in `client->ioreqs_map`, and wakes the client. Kernel clients run `ioreq_task()` in a kthread; the default client is consumed by userspace through waits and completion ioctls. Persistent runtime state is the pinned `vm->ioreq_page`, `vm->ioreq_buf`, per-client range lists, pending bitmaps, and global workqueue/interrupt handler.

## Dependencies and Integration
Integrates with ACRN hypercalls `hcall_set_ioreq_buffer()` and `hcall_notify_req_finish()`, the ACRN VM list in `vm.c`, ioctl paths in `hsm.c`, and client modules such as ioeventfd. It uses `pin_user_pages_fast(FOLL_WRITE | FOLL_LONGTERM)`, waitqueues, kthreads, rwlocks, spinlocks, and workqueues.

## Risks and Test Signals
Risk is concentrated in shared-page ordering, client teardown races, stale default-client requests during reset, and long-term page pin lifetime. `ioreq_pause()` removes the interrupt handler and drains work before client removal, which is the main teardown guard. Tests should exercise multiple vCPUs, default and kernel clients, CF8/CFC reads and writes, reset-time clearing, client destroy while requests are pending, and failure paths for page pinning and `hcall_set_ioreq_buffer()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/ioreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/irqfd.c -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/irqfd.c

## Purpose
Provides ACRN irqfd support: userspace attaches an eventfd to a VM and each eventfd signal injects an MSI into the User VM.

## APIs, Types, and Functions
The core type is `struct hsm_irqfd`, carrying the VM, eventfd context, waitqueue entry, poll table, shutdown work, list node, and `struct acrn_msi_entry`. Public entry points are `acrn_irqfd_init()`, `acrn_irqfd_config()`, and `acrn_irqfd_deinit()`. Internal helpers are `acrn_irqfd_assign()`, `acrn_irqfd_deassign()`, `hsm_irqfd_wakeup()`, `hsm_irqfd_poll_func()`, `hsm_irqfd_shutdown()`, `hsm_irqfd_shutdown_work()`, and `acrn_irqfd_inject()`.

## Control Flow and State
VM creation initializes `vm->irqfds`, `vm->irqfds_lock`, and a per-VM irqfd workqueue. Assignment resolves the supplied fd, obtains an eventfd context, installs a custom waitqueue callback through `vfs_poll()`, rejects duplicate eventfd contexts, and injects immediately if the eventfd was already readable. On wakeup, `POLLIN` calls `acrn_msi_inject()` and `POLLHUP` schedules shutdown work. Deassignment looks up by eventfd and removes the waitqueue entry under `irqfds_lock`.

## Dependencies and Integration
The module depends on Linux `eventfd`, `poll`, `file` fd wrappers, VM-local mutexes/workqueue state, and the ACRN MSI injection helper implemented in `vm.c`.

## Risks and Test Signals
Important risks are eventfd lifetime races, shutdown work running after deinit, duplicate fd handling, and injection from waitqueue callback context. Notably `acrn_irqfd_deinit()` destroys `vm->irqfd_wq` before list shutdown; test coverage should check POLLHUP/deinit ordering, repeated assign/deassign, duplicate eventfd rejection, pending event injection at assignment, and invalid fd errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/irqfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/mm.c -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/mm.c

## Purpose
Manages ACRN User VM memory mappings. It translates userspace or MMIO memory descriptors into hypervisor memory-region batches and keeps enough Service VM-side state to unpin and unmap RAM later.

## APIs, Types, and Functions
Exports `acrn_mm_region_add()`, `acrn_mm_region_del()`, `acrn_vm_memseg_map()`, `acrn_vm_memseg_unmap()`, `acrn_vm_ram_map()`, and `acrn_vm_all_ram_unmap()`. Internal `modify_region()` wraps a single `vm_memory_region_op` inside `vm_memory_region_batch` for `hcall_set_memory_regions()`. State uses `struct vm_memory_mapping` entries stored in `vm->regions_mapping`.

## Control Flow and State
MMIO maps are direct `ACRN_MEM_TYPE_UC` add/delete operations. RAM maps first handle `VM_PFNMAP` VMAs by validating contiguous, writable, reserved PFNs and mapping them directly. Normal userspace memory is pinned with `pin_user_pages_fast(FOLL_WRITE | FOLL_LONGTERM)`, `vmap()`ed into the Service VM, recorded under `regions_mapping_lock`, coalesced by compound-page order into region operations, and submitted to the hypervisor. On hypercall failure, the code unwinds the mapping count, vmap, and page pins. `acrn_vm_all_ram_unmap()` walks recorded mappings and releases all kernel mappings and page references.

## Dependencies and Integration
Depends on Linux mm primitives, GUP long-term pins, `vmap()/vunmap()`, PFNMAP helpers, and ACRN memory hypercall definitions. It is invoked from ACRN ioctl handling and VM destruction.

## Risks and Test Signals
Risks include long-term pin accounting, `regions_mapping_count` slot exhaustion, partial rollback after hypervisor add failure, PFNMAP validation accepting only safe reserved contiguous memory, and lack of reset of `regions_mapping_count` after full unmap. Tests should cover RAM and MMIO map/unmap, PFNMAP success/failure, non-page-aligned lengths, compound pages, exceeding `ACRN_MEM_MAPPING_MAX`, and destroy after partially failed mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/vm.c -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/vm.c

## Purpose
Owns ACRN VM lifecycle and MSI injection plumbing for the HSM driver.

## APIs, Types, and Functions
Defines global `acrn_vm_list` and `acrn_vm_list_lock`. Exports `acrn_vm_create()`, `acrn_vm_destroy()`, and `acrn_msi_inject()`.

## Control Flow and State
`acrn_vm_create()` calls `hcall_create_vm()`, initializes region and ioreq client locks/lists, stores VMID/vCPU count, initializes the shared ioreq page, adds the VM to the global list, and initializes ioeventfd and irqfd subsystems. `acrn_vm_destroy()` is idempotent via `ACRN_VM_FLAG_DESTROYED`, destroys the hypervisor VM first, removes the VM from the global list, deinitializes ioeventfd, irqfd, ioreq, monitor-page, and RAM mappings, then invalidates `vmid`. `acrn_msi_inject()` allocates an MSI entry with `GFP_ATOMIC`, fills address/data, and calls `hcall_inject_msi()`.

## Dependencies and Integration
This file coordinates with all ACRN HSM submodules and hypercalls. It is invoked from the `/dev/acrn_hsm` ioctl lifecycle in `hsm.c`.

## Risks and Test Signals
Creation can leak submodule state if `acrn_ioeventfd_init()` or `acrn_irqfd_init()` were to fail because return values are not checked. Destruction order matters because request dispatch walks the global list. Tests should validate repeated destroy, failure after ioreq init, VM list visibility during dispatch, MSI injection from irqfd context, and resource cleanup after mapped RAM and active clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/Kconfig

## Purpose
Top-level Kconfig menu for confidential-computing collateral under `drivers/virt/coco`.

## APIs, Types, and Functions
It conditionally sources EFI secret, pKVM guest, SEV guest, TDX guest, Arm CCA guest, and shared guest Kconfig files when `VIRT_DRIVERS` is enabled. It also declares boolean `TSM`, the class-device switch for `tsm-core.c`.

## Control Flow and State
There is no runtime state. Build-time state is the selected set of confidential-computing features and their transitive selects such as `TSM_REPORTS` and `TSM_MEASUREMENTS`.

## Dependencies and Integration
Feeds the `drivers/virt/coco/Makefile` object selection. It integrates multiple architecture-specific guest drivers under one menu.

## Risks and Test Signals
Risk is misconfigured symbol naming. The Makefile uses `CONFIG_INTEL_TDX_GUEST` for the `tdx-guest/` directory, while the TDX guest sub-Kconfig defines `TDX_GUEST_DRIVER`; this relies on an external architecture symbol to descend into the directory. Build tests should cover x86 TDX, AMD SEV, arm64 CCA, pKVM, EFI secret, and `CONFIG_TSM` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/Makefile

## Purpose
Build dispatch for confidential-computing support.

## APIs, Types, and Functions
Selects subdirectories and `tsm-core.o`: `efi_secret/`, `pkvm-guest/`, `sev-guest/`, `tdx-guest/`, `arm-cca-guest/`, `guest/`, and `tsm-core.o`.

## Control Flow and State
No runtime control flow. It maps Kconfig symbols to build artifacts.

## Dependencies and Integration
`CONFIG_TSM_GUEST` pulls in shared report/measurement helpers; vendor drivers select those shared symbols. `CONFIG_TSM` builds the class device used by PCI TSM integrations.

## Risks and Test Signals
Build risk is symbol mismatch or missing subdirectory dependencies. Test by building representative configs with all symbols as built-in and as modules where allowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/Kconfig

## Purpose
Declares Arm CCA guest attestation support.

## APIs, Types, and Functions
`ARM_CCA_GUEST` is a tristate depending on `ARM64` and selecting `TSM_REPORTS`.

## Control Flow and State
Build-time only. Enables `arm-cca-guest.o` as module or built-in and makes the shared configfs report frontend available.

## Dependencies and Integration
Runtime code depends on Arm RSI support and TSM report registration.

## Risks and Test Signals
The help text has a minor grammar issue but the functional risk is ensuring this symbol is not enabled on non-Realm systems; the module itself returns `-ENODEV` when not in Realm world. Build-test arm64 with `CONFIG_TSM_REPORTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/Makefile

## Purpose
Builds the Arm CCA guest TSM provider.

## APIs, Types, and Functions
Maps `CONFIG_ARM_CCA_GUEST` to `arm-cca-guest.o`.

## Control Flow and State
No runtime state; it is a single-object module rule.

## Dependencies and Integration
Consumed by the parent CoCo Makefile and Kconfig.

## Risks and Test Signals
Build with `ARM_CCA_GUEST=m` and built-in on arm64 to verify module naming and TSM symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/arm-cca-guest.c -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/arm-cca-guest.c

## Purpose
Implements an Arm CCA Realm TSM report provider. It turns a configfs TSM inblob challenge into an attestation token generated by the Realm Management Monitor through RSI calls.

## APIs, Types, and Functions
Key type is `struct arm_cca_token_info`, carrying challenge, granule PA, offset, and RSI result. Main functions are `arm_cca_report_new()`, `arm_cca_attestation_init()`, `arm_cca_attestation_continue()`, `arm_cca_guest_init()`, and `arm_cca_guest_exit()`. It registers `arm_cca_tsm_ops` with `tsm_report_register()`.

## Control Flow and State
Initialization checks `is_realm_world()` before registering. `arm_cca_report_new()` validates challenge length 32..64 bytes, chooses the current CPU, runs RSI init on that CPU using `smp_call_function_single()`, allocates a maximum-size token buffer and a single RSI granule bounce buffer, repeatedly calls RSI continue on the same CPU, copies granule chunks to the final outblob, and publishes `report->outblob_len`.

## Dependencies and Integration
Depends on Arm SMCCC/RSI (`rsi_attestation_token_init/continue`, `RSI_GRANULE_SIZE`), SMP call routing, and shared TSM report configfs.

## Risks and Test Signals
Same-CPU execution is essential; CPU hotplug or preemption-sensitive behavior should be tested. Risks include oversized RMM output, partial token on error, and correct freeing of the granule page. Tests should validate challenge length bounds, `RSI_INCOMPLETE` loops, negative RSI results, module autoload modalias, and unregister while no report items are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/arm-cca-guest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/Kconfig

## Purpose
Adds build configuration for the EFI confidential-computing secret-area securityfs driver.

## APIs, Types, and Functions
`EFI_SECRET` is a tristate depending on EFI and x86_64 or arm64, selecting `EFI_COCO_SECRET` and `SECURITYFS`.

## Control Flow and State
Build-time selection only. Runtime state is created by `efi_secret.c` when the platform exposes the EFI secret area.

## Dependencies and Integration
Integrates with EFI config-table discovery, encrypted memory mapping, and securityfs.

## Risks and Test Signals
Build and boot tests should cover EFI absent, EFI secret area absent, empty secret table, and module build. Security-sensitive tests should verify deleted secrets are wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/Makefile

## Purpose
Builds the EFI secret-area driver.

## APIs, Types, and Functions
Maps `CONFIG_EFI_SECRET` to `efi_secret.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Used by the CoCo parent Makefile.

## Risks and Test Signals
Build both built-in and module variants and verify module alias `platform:efi_secret` comes from the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/efi_secret.c -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/efi_secret.c

## Purpose
Exposes firmware-injected confidential-computing secrets as read/delete files under `securityfs` at `secrets/coco`.

## APIs, Types, and Functions
Important structures are `struct efi_secret`, `struct secret_header`, and `struct secret_entry`. Main functions are `efi_secret_probe()`, `efi_secret_map_area()`, `efi_secret_securityfs_setup()`, `efi_secret_bin_file_show()`, `efi_secret_unlink()`, `wipe_memory()`, `efi_secret_securityfs_teardown()`, and `efi_secret_unmap_area()`.

## Control Flow and State
Probe maps the EFI CoCo secret descriptor from `efi.coco_secret`, validates base and size, maps the actual secret area encrypted, validates the table header GUID and reported length, creates `securityfs` directories, then creates up to 64 files named by secret GUID. Reading a file streams the secret bytes through seq_file. Unlinking a file zeros secret data, flushes cache on x86, marks the entry GUID `NULL_GUID`, clears `inode->i_private`, and delegates to `simple_unlink()`. Global state is `the_efi_secret`, containing the mapped region and root dentry.

## Dependencies and Integration
Depends on EFI CoCo secret table support, `ioremap_encrypted()`, securityfs, seq_file helpers, GUID helpers, and platform-driver binding named `efi_secret`.

## Risks and Test Signals
Security risks are stale secret exposure, incomplete wiping, malformed table walking, and teardown after partial securityfs creation. The parent `secrets` directory is removed via `securityfs_remove(s->secrets_dir)`, relying on recursive cleanup. Tests should cover invalid GUID, short/oversized table length, corrupt entry length, more than 64 entries, read-after-delete, and x86 cache flushing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/efi_secret.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/guest/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/guest/Kconfig

## Purpose
Declares shared guest-side TSM support symbols.

## APIs, Types, and Functions
`TSM_GUEST` is a base bool. `TSM_REPORTS` is a tristate selecting `TSM_GUEST` and `CONFIGFS_FS`. `TSM_MEASUREMENTS` is a bool selecting `TSM_GUEST` and `CRYPTO_HASH_INFO`.

## Control Flow and State
Build-time only. It gates the configfs attestation report frontend and sysfs measurement-register helper.

## Dependencies and Integration
SEV, TDX, and Arm CCA providers select `TSM_REPORTS`; TDX selects measurements.

## Risks and Test Signals
The line `select CONFIGFS_FS` is unusual because Kconfig select targets are typically bare symbol names; build validation should confirm the tree accepts it as intended. Test all vendor providers that depend on this shared layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/guest/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/guest/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/guest/Makefile

## Purpose
Builds shared guest TSM objects.

## APIs, Types, and Functions
`CONFIG_TSM_REPORTS` builds `tsm_report.o` from `report.o`; `CONFIG_TSM_MEASUREMENTS` builds `tsm-mr.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Used by vendor drivers through exported symbols from `report.c` and `tsm-mr.c`.

## Risks and Test Signals
Build tests should cover `TSM_REPORTS=m` with provider modules and built-in provider combinations to catch symbol visibility issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/guest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/guest/report.c -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/guest/report.c

## Purpose
Implements the common TSM attestation report configfs frontend. It lets userspace create `configfs/tsm/report/<item>` instances, write report parameters and an input blob, and read provider-generated report, aux, or manifest blobs.

## APIs, Types, and Functions
Exports `tsm_report_register()` and `tsm_report_unregister()`. Core types are global `provider` (`ops`, private data, active item count) and per-item `struct tsm_report_state` wrapping `struct tsm_report`. Store/read handlers cover `privlevel`, `privlevel_floor`, `service_provider`, `service_guid`, `service_manifest_version`, `inblob`, `generation`, `provider`, `outblob`, `auxblob`, and `manifestblob`.

## Control Flow and State
Module init registers configfs subsystem `tsm` and default group `report`. Providers register one active `struct tsm_report_ops`; registration is rejected when another provider is active or configfs items already exist. Each write takes `tsm_rwsem` for write, advances `write_generation`, and mutates the descriptor. Reads first try a cached report under read lock; if stale, the slow path takes write lock, clears old blobs, calls `ops->report_new()`, updates `read_generation`, and copies requested blob data. Visibility callbacks defer attribute exposure to the active provider.

## Dependencies and Integration
Depends on configfs, shared `linux/tsm.h`, provider modules such as SEV, TDX, and Arm CCA, and cleanup guard macros.

## Risks and Test Signals
Risks include provider unregister while items exist, generation counter wrap guard, stale cached blobs, input blob length validation delegated to providers, and attribute visibility changing with provider state. Tests should cover no-provider errors, concurrent reads/writes, repeated configfs items, provider conflict, unregister with items present, and provider-specific visibility matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/guest/report.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/guest/tsm-mr.c -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/guest/tsm-mr.c

## Purpose
Provides a reusable sysfs binary-attribute generator for TSM measurement registers.

## APIs, Types, and Functions
Exports `tsm_mr_create_attribute_group()` and `tsm_mr_free_attribute_group()`. Internal `struct tm_context` owns the generated attribute group, MR bin attributes, source `struct tsm_measurements`, cache sync flag, and rwsem. File operations are `tm_digest_read()` and `tm_digest_write()`.

## Control Flow and State
Creation validates MR definitions, required callbacks, names, hash IDs, and duplicate generated names. It allocates one context and one combined attribute/name block. Read locks the context, refreshes live MRs on a stale cache by upgrading to write lock, copies the requested digest slice, and traces reads. Writes require a full-size write at offset zero, call provider `write()`, mark the cache stale, and trace. Freeing releases the generated bin-attribute array and context.

## Dependencies and Integration
Depends on `linux/tsm-mr.h`, crypto hash-name metadata, sysfs binary attributes, and tracepoints from `trace/events/tsm_mr.h`. TDX uses it for RTMR/MR exposure.

## Risks and Test Signals
Risks include provider freeing MR backing storage before removing the group, stale-cache semantics being global rather than per-MR, and write callbacks extending security-sensitive registers. Tests should validate invalid MR definitions, duplicate names, live refresh behavior, partial write rejection, tracepoints, and TDX group teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/guest/tsm-mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/Kconfig

## Purpose
Declares arm64 pKVM protected guest support.

## APIs, Types, and Functions
`ARM_PKVM_GUEST` is a bool depending on `ARM64` and `DMA_RESTRICTED_POOL`.

## Control Flow and State
Build-time only. The driver registers memory encryption/decryption and optional MMIO guard hooks at runtime.

## Dependencies and Integration
Integrates with arm64 protected KVM SMCCC services and DMA restricted-pool support.

## Risks and Test Signals
Build-test arm64 protected guest configs and ensure unsupported systems leave the hooks unregistered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/Makefile

## Purpose
Builds the arm64 pKVM guest helper.

## APIs, Types, and Functions
Maps `CONFIG_ARM_PKVM_GUEST` to `arm-pkvm-guest.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Included by the parent CoCo Makefile.

## Risks and Test Signals
Build with `ARM_PKVM_GUEST=y`; it is bool-only, so module unload paths do not apply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/arm-pkvm-guest.c -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/arm-pkvm-guest.c

## Purpose
Initializes hypervisor services for arm64 pKVM protected guests: memory share/unshare operations and optional MMIO guard registration.

## APIs, Types, and Functions
Public entry is `pkvm_init_hyp_services()`. Key helpers are `arm_smccc_do_one_page()`, `__set_memory_range()`, `pkvm_set_memory_encrypted()`, `pkvm_set_memory_decrypted()`, and `mmio_guard_ioremap_hook()`. It registers `arm64_mem_crypt_ops`.

## Control Flow and State
Initialization checks that required KVM hypervisor service IDs exist, queries the pKVM granule size, rejects impossible granules larger than a page, stores `pkvm_granule`, and registers memory encryption ops. Memory transitions iterate each page and each pKVM granule with SMCCC calls. The MMIO guard hook filters device mappings, rounds to page boundaries, and asks the hypervisor to guard every page.

## Dependencies and Integration
Depends on Arm SMCCC, arm64 hypervisor service discovery, `arm64_mem_crypt_ops_register()`, and `arm64_ioremap_prot_hook_register()`.

## Risks and Test Signals
Risks are partial memory-range transitions, ignored MMIO guard failures beyond WARN, and assumptions about granule dividing a page. Tests should cover service absence, bad granule return, memory share/unshare failure, MMIO mappings with device and non-device pgprot values, and DMA interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/arm-pkvm-guest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/Kconfig

## Purpose
Declares the AMD SEV guest driver.

## APIs, Types, and Functions
`SEV_GUEST` is a tristate, defaults to module, depends on `AMD_MEM_ENCRYPT`, and selects `TSM_REPORTS`.

## Control Flow and State
Build-time only. Runtime exposes `/dev/sev-guest` and registers a TSM provider when running as an SEV-SNP guest.

## Dependencies and Integration
Depends on AMD memory encryption and PSP/SNP guest messaging support.

## Risks and Test Signals
Test module and built-in builds with and without SNP guest platform attributes. Verify TSM report symbols resolve when built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/Makefile

## Purpose
Builds the AMD SEV guest driver.

## APIs, Types, and Functions
Maps `CONFIG_SEV_GUEST` to `sev-guest.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Included by the parent CoCo Makefile.

## Risks and Test Signals
Build as `m` and `y`, especially with `TSM_REPORTS=m/y` compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/sev-guest.c -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/sev-guest.c

## Purpose
Provides AMD SEV-SNP guest userspace and TSM interfaces for attestation reports, derived keys, extended reports with certificates, and optional SVSM service attestation.

## APIs, Types, and Functions
Core state is `struct snp_guest_dev` with a device, miscdevice, and `struct snp_msg_desc`. Important functions are `snp_guest_ioctl()`, `get_report()`, `get_derived_key()`, `get_ext_report()`, `sev_report_new()`, `sev_svsm_report_new()`, visibility callbacks, `sev_guest_probe()`, and `sev_guest_remove()`. It exposes `/dev/sev-guest` ioctls `SNP_GET_REPORT`, `SNP_GET_DERIVED_KEY`, and `SNP_GET_EXT_REPORT`, and registers `sev_tsm_report_ops`.

## Control Flow and State
Probe requires `CC_ATTR_GUEST_SEV_SNP`, allocates and initializes the SNP message descriptor using `vmpck_id`, registers TSM ops, then registers the misc device. Ioctls copy a common request struct, require nonzero message version, and dispatch to encrypted SNP guest requests. Extended reports allocate a shared decrypted certificate buffer when requested, send a VMGEXIT extended guest request, copy certs and report back, and restore encryption before freeing. TSM report generation either calls SVSM attestation when `service_provider=svsm` or issues an SNP extended report, validates the response header, copies the report into `outblob`, and optionally exposes certificate data as `auxblob`.

## Dependencies and Integration
Depends on AMD SNP guest messaging (`snp_msg_*`, `snp_send_guest_request()`), SEV/SVM VMGEXIT definitions, memory encryption transitions, miscdevice, configfs TSM, and optional SVSM attestation helpers.

## Risks and Test Signals
Risks are sensitive derived-key buffer wiping, shared-page encryption restoration failures, certificate-size truncation, VMPCK selection and invalid-key handling, and provider registration ordering before `snp_dev->msg_desc` assignment. Tests should cover all ioctls, bad user pointers, zero message version, invalid cert lengths, VMM invalid-length feedback, SVSM retry resizing, TSM attr visibility under VMPL, and cleanup on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/sev-guest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/Kconfig

## Purpose
Declares Intel TDX guest userspace driver support.

## APIs, Types, and Functions
`TDX_GUEST_DRIVER` is a tristate depending on `INTEL_TDX_GUEST` and selecting `TSM_REPORTS` and `TSM_MEASUREMENTS`.

## Control Flow and State
Build-time only. Runtime exposes a misc device, TSM report provider, and measurement sysfs group.

## Dependencies and Integration
Requires architecture TDX guest support plus shared TSM report and measurement helpers.

## Risks and Test Signals
Build-test with `INTEL_TDX_GUEST` enabled. Confirm parent Makefile descends into this directory under the architecture symbol and that `TDX_GUEST_DRIVER` controls object compilation inside it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/Makefile

## Purpose
Builds the Intel TDX guest driver.

## APIs, Types, and Functions
Maps `CONFIG_TDX_GUEST_DRIVER` to `tdx-guest.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Included from the CoCo parent directory when TDX guest support is selected.

## Risks and Test Signals
Build `TDX_GUEST_DRIVER=m/y`, especially with the parent directory selected by `CONFIG_INTEL_TDX_GUEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/tdx-guest.c -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/tdx-guest.c

## Purpose
Implements Intel TDX guest report, quote, and measurement-register interfaces.

## APIs, Types, and Functions
User API is a miscdevice named by `KBUILD_MODNAME` with ioctl `TDX_CMD_GET_REPORT0`. TSM report provider is `tdx_tsm_ops` using `tdx_report_new()`. Measurement support uses `tdx_mrs`, `tdx_measurements`, `tdx_mr_init()`, `tdx_mr_refresh()`, and `tdx_mr_extend()`. Quote helpers include `alloc_quote_buf()`, `free_quote_buf()`, `tdx_report_new_locked()`, and `wait_for_quote_completion()`.

## Control Flow and State
Initialization checks CPU feature `X86_FEATURE_TDX_GUEST`, initializes the TDREPORT buffer and measurement attribute group, registers the misc device, allocates a shared decrypted quote buffer, and registers TSM ops. `tdx_do_report()` serializes TDREPORT generation under `mr_lock`, copies optional reportdata, performs `tdx_mcall_get_report0()`, and copies the report out. TSM quote generation serializes under `quote_lock`, rejects in-flight buffers, embeds a TDREPORT in the quote buffer, invokes `tdx_hcall_get_quote()`, polls status for up to `getquote_timeout`, validates `out_len`, and copies quote data to `outblob`. RTMR extension reuses the aligned REPORTDATA area under the same MR lock.

## Dependencies and Integration
Depends on x86 TDX module calls, TDX hypercalls, memory encryption transitions for the shared quote buffer, miscdevice, shared TSM report frontend, and TSM measurement sysfs helpers.

## Risks and Test Signals
Risks include quote buffer leaks if decryption succeeds but later paths fail, in-flight quote ownership after timeout, shared `tdx_report_buf` reuse between report and RTMR extension, and MR offset-to-pointer patching. Tests should cover feature absence, ioctl report generation, TSM quote timeout and oversized output, interruptible locks, RTMR extension serialization, measurement sysfs reads/writes, and encryption restoration on module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/tdx-guest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/tsm-core.c -->
# sources/distributed-fs/ceph-client/drivers/virt/coco/tsm-core.c

## Purpose
Implements a generic TEE Security Manager device class and registration API, with optional PCI TSM integration.

## APIs, Types, and Functions
Exports `tsm_register()`, `tsm_unregister()`, and `find_tsm_dev()`. Internal helpers are `alloc_tsm_dev()`, `tsm_register_pci_or_reset()`, `match_id()`, and `tsm_release()`. Global state is `tsm_class` and `tsm_ida`.

## Control Flow and State
Module init registers class `tsm`. Registration allocates a `struct tsm_dev`, allocates an ID, initializes an embedded `struct device`, names it `tsm%d`, adds it to the class, optionally registers PCI TSM ops, and emits a `KOBJ_CHANGE` uevent when PCI TSM becomes available. Unregistration reverses PCI TSM registration if present and unregisters the device; release frees the ID and memory.

## Dependencies and Integration
Depends on Linux device classes, IDA, cleanup annotations, and `pci_tsm_register()/pci_tsm_unregister()`.

## Risks and Test Signals
Risks include reference lifetime through `find_tsm_dev()`, PCI registration failure after device add, and uevent ordering. Tests should cover register/unregister cycles, failed `dev_set_name()`/`device_add()`, PCI ops failure rollback, ID reuse, and class unregister after devices are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/coco/tsm-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/fsl_hypervisor.c -->
# sources/distributed-fs/ceph-client/drivers/virt/fsl_hypervisor.c

## Purpose
Provides Freescale hypervisor management through a misc device, doorbell event delivery, shutdown handling, partition failover notifications, and partition/device-tree management ioctls.

## APIs, Types, and Functions
Userspace API is miscdevice `fsl-hv` with `fsl_hv_ioctl()`, `fsl_hv_read()`, `fsl_hv_poll()`, `fsl_hv_open()`, and `fsl_hv_close()`. Ioctl helpers include partition restart/status/start/stop, remote/local memcpy, doorbell send, and device-tree property get/set. Kernel notifier exports are `fsl_hv_failover_register()` and `fsl_hv_failover_unregister()`. Runtime queue types are `struct doorbell_queue` and `struct doorbell_isr`.

## Control Flow and State
Init verifies `/hypervisor` has `fsl,hv-version`, registers the misc device, initializes global doorbell queue and ISR lists, scans compatible doorbell nodes, maps IRQs, and registers normal, shutdown, or threaded state-change handlers. Each open creates a per-file ring buffer. Doorbell IRQs enqueue handles into all open queues and wake readers; state-change IRQs also query partition status and call blocking notifiers from the threaded handler when stopped. Ioctls wrap Freescale hypercalls, copying parameters and return codes to userspace. The memcpy ioctl pins user pages, builds an aligned hypervisor scatterlist, calls `fh_partition_memcpy()`, and releases pages.

## Dependencies and Integration
Depends on Power/Freescale hypercall ABI (`asm/fsl_hcalls.h`), OF device tree, IRQ APIs, miscdevice, notifier chains, GUP, and reboot poweroff.

## Risks and Test Signals
Risks include fixed 16-entry doorbell queues dropping events silently when full, memory barriers around lock-light queue writes, ioctl parameter validation, GUP write direction in memcpy, and IRQ cleanup after partial init. Tests should cover doorbell read blocking/nonblocking/poll, queue overflow, all ioctls, malformed DT nodes, shutdown doorbell, state-change notifier ordering, and remote memcpy with misaligned buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/fsl_hypervisor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/Kconfig

## Purpose
Declares Amazon Nitro Enclaves lifetime-management driver and KUnit tests.

## APIs, Types, and Functions
`NITRO_ENCLAVES` is a tristate depending on arm64 or x86, CPU hotplug, PCI, and SMP. `NITRO_ENCLAVES_MISC_DEV_TEST` is a bool for KUnit tests depending on `NITRO_ENCLAVES` and `KUNIT=y`.

## Control Flow and State
Build-time only. Enables the PCI and misc-device driver pair.

## Dependencies and Integration
Runtime depends on CPU hotplug and PCI; tests are compiled into `ne_misc_dev.c` when selected.

## Risks and Test Signals
Build-test module and built-in variants on x86 and arm64. KUnit should be enabled in UML/qemu-style test kernels only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/Makefile

## Purpose
Builds the Nitro Enclaves driver.

## APIs, Types, and Functions
`CONFIG_NITRO_ENCLAVES` builds module `nitro_enclaves.o` from `ne_pci_dev.o` and `ne_misc_dev.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
The misc-device source includes KUnit test code conditionally; both object files share headers and global `ne_devs`.

## Risks and Test Signals
Build with KUnit test enabled and disabled to ensure the static helper under test remains visible through inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev.c -->
# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev.c

## Purpose
Implements the user-facing Nitro Enclaves misc device and per-enclave anonymous file API. It manages CPU-pool donation, enclave slot creation, vCPU assignment, hugetlb memory registration, enclave start, event polling, and cleanup.

## APIs, Types, and Functions
Global API is `/dev/nitro_enclaves` with `NE_CREATE_VM`, returning an anon inode using `ne_enclave_fops`. Enclave ioctls are `NE_ADD_VCPU`, `NE_GET_IMAGE_LOAD_INFO`, `NE_SET_USER_MEMORY_REGION`, and `NE_START_ENCLAVE`. Major helpers include `ne_setup_cpu_pool()`, `ne_teardown_cpu_pool()`, `ne_set_kernel_param()`, CPU selection/check helpers, `ne_set_user_memory_region_ioctl()`, `ne_merge_phys_contig_memory_regions()`, `ne_start_enclave_ioctl()`, `ne_enclave_release()`, and `ne_create_vm_ioctl()`.

## Control Flow and State
Module init initializes the CPU-pool mutex and registers the NE PCI driver. The `ne_cpus` module parameter, settable only by `CAP_SYS_ADMIN`, parses a CPU list, requires online CPUs from one NUMA node, excludes CPU0 and siblings, requires full cores, offlines the pool, and records available thread masks by core. `NE_CREATE_VM` checks CPU availability, allocates enclave state and cpumasks, obtains an fd and anon file, asks the PCI device for a slot, initializes per-enclave state, links it into the PCI device enclave list, and returns slot UID plus fd. Enclave ioctls add vCPUs from the pool or explicit IDs, register 2 MiB-aligned hugetlb memory from the same NUMA node, merge physically contiguous chunks before `SLOT_ADD_MEM`, validate minimum memory/full cores/vCPU count, and start the enclave. Release stops a running enclave, frees the slot, returns CPUs, drops pinned pages, removes list entries, and frees state.

## Dependencies and Integration
Depends on `ne_do_request()` from `ne_pci_dev.c`, CPU hotplug, topology sibling masks, hugetlb pages, anon inodes, miscdevice, vsock CID ABI, Linux Nitro Enclaves UAPI, and shared global `ne_devs`.

## Risks and Test Signals
High-risk areas are CPU hotplug rollback, locking order between PCI enclave list and per-enclave mutex, page references after partial `SLOT_ADD_MEM` failure, ensuring all sibling CPUs are assigned before start, stale `has_event` poll semantics, and `ne_devs.ne_pci_dev` availability during ioctl/release. Existing KUnit only covers physical-region merge behavior. Additional tests should cover CPU-pool parsing and teardown, enclave create failure cleanup, memory overlap and NUMA rejection, vCPU auto/allocation, start validation, release after running and after partial setup, PCI command failures, and event wakeups from `ne_pci_dev.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev.h -->
# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev.h

## Purpose
Declares shared Nitro Enclaves misc-device state used by the PCI and misc sides of the driver.

## APIs, Types, and Functions
Defines `struct ne_mem_region`, `struct ne_enclave`, `enum ne_state`, and `struct ne_devs`, and declares global `ne_devs`.

## Control Flow and State
No executable flow. The types describe persistent per-enclave state: memory-region list and pinned pages, event waitqueue and flag, max memory regions, mm ownership, vCPU masks, slot UID, NUMA node, threads-per-core masks, and state values `INIT`, `RUNNING`, and `STOPPED`.

## Dependencies and Integration
Includes `ne_pci_dev.h` and Linux cpumask/list/misc/mm/pci/wait primitives. `ne_pci_dev.c` updates enclave state on events; `ne_misc_dev.c` owns allocation and cleanup.

## Risks and Test Signals
Risk centers on shared state lifetime across PCI removal, enclave fd release, and event work. Tests should assert that all fields are initialized before list insertion and that event work cannot access freed enclave structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev_test.c -->
# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev_test.c

## Purpose
KUnit tests for Nitro Enclaves physical contiguous memory-region merge helper.

## APIs, Types, and Functions
Defines `struct ne_phys_regions_test`, a table of cases, `ne_misc_dev_test_merge_phys_contig_memory_regions()`, KUnit cases, and suite `ne_misc_dev_test`.

## Control Flow and State
The test allocates a fixed region array, applies a sequence of add/merge attempts to `ne_merge_phys_contig_memory_regions()`, and verifies return code, region count, and last region start/length. Cases cover unaligned address, unaligned size, separate valid regions, adjacent merge, and rejection that leaves prior state intact.

## Dependencies and Integration
This file is included directly by `ne_misc_dev.c` under `CONFIG_NITRO_ENCLAVES_MISC_DEV_TEST`, giving it access to static helper definitions.

## Risks and Test Signals
Coverage is useful but narrow. It does not test overflow at maximum region count, non-last-region adjacency, or memory-registration ioctl rollback. KUnit should be run with `CONFIG_KUNIT=y` and the test symbol enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_pci_dev.c -->
# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_pci_dev.c

## Purpose
Implements the PCI-facing Nitro Enclaves command transport and event handling. It binds the Amazon NE PCI device, maps MMIO registers, manages MSI-X vectors, serializes commands, and registers the misc device after hardware setup.

## APIs, Types, and Functions
Exports `ne_do_request()` and `struct pci_driver ne_pci_driver`. Internal helpers include `ne_submit_request()`, `ne_retrieve_reply()`, `ne_wait_for_reply()`, reply/event IRQ handlers, `ne_event_work_handler()`, MSI-X setup/teardown, PCI enable/disable, probe/remove/shutdown.

## Control Flow and State
Probe allocates `struct ne_pci_dev`, enables PCI, requests regions, maps BAR 3, sets driver data, configures MSI-X reply and event vectors, resets/enables device version, initializes command waitqueue/list/mutexes, sets global `ne_devs.ne_pci_dev`, and registers the misc device. `ne_do_request()` validates command type and payload sizes, locks `pci_dev_mutex`, clears reply flag, writes request bytes and command register, waits up to 120 seconds for reply IRQ, reads reply, clears flag, and converts device `rc` to Linux error. Event IRQ schedules work; work scans all running enclaves, asks `SLOT_INFO`, updates state, sets `has_event`, and wakes the enclave waitqueue when state changes.

## Dependencies and Integration
Depends on PCI/MSI-X, mapped NE MMIO ABI from `ne_pci_dev.h`, the misc-side enclave list and global `ne_devs`, Linux waitqueues/workqueues, and Nitro UAPI command semantics.

## Risks and Test Signals
Risks include long uninterruptible command waits, event work racing with enclave release/removal, global `ne_devs` lifetime, MSI-X vector count assumptions, and device disable timeout. Tests should cover invalid command sizes, reply timeout, negative device reply, event state change propagation, probe rollback at every failure label, remove/shutdown with active enclaves, and concurrent `ne_do_request()` callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_pci_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_pci_dev.h -->
# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_pci_dev.h

## Purpose
Defines the Nitro Enclaves PCI device ABI, command payloads, reply structure, device state, and exported command helper.

## APIs, Types, and Functions
Important constants include PCI device ID `0xe4c1`, BAR `3`, MMIO offsets `NE_ENABLE`, `NE_VERSION`, `NE_COMMAND`, `NE_EVTCNT`, send/receive buffers, sizes, and MSI-X vectors. It defines `enum ne_pci_dev_cmd_type`, request structs for enclave and slot operations, `struct ne_pci_dev_cmd_reply`, `struct ne_pci_dev`, declaration of `ne_do_request()`, and external `ne_pci_driver`.

## Control Flow and State
No executable flow. The ABI state includes command reply availability, enclave list, event workqueue, MMIO base, PCI mutex, and backing `pci_dev`.

## Dependencies and Integration
Consumed by both `ne_pci_dev.c` and `ne_misc_dev.c`; command structs mirror Nitro Hypervisor expectations and must stay within 240-byte MMIO payload buffers.

## Risks and Test Signals
Risks are ABI drift, padding/size mismatches, endian assumptions, and command sizes exceeding MMIO buffers. Compile-time size checks would be valuable. Tests should validate every request struct size against `NE_SEND_DATA_SIZE` and reply size against `NE_RECV_DATA_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_pci_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/Kconfig

## Purpose
Declares VirtualBox guest integration support.

## APIs, Types, and Functions
`VBOXGUEST` is a tristate depending on arm64/x86/compile-test, PCI, INPUT, and HAS_IOPORT.

## Control Flow and State
Build-time only. Enables the VirtualBox Guest PCI driver and related guest integration IPC.

## Dependencies and Integration
The help notes integration with vboxfs and recommends VBOXVIDEO for display support. The Makefile builds the Linux wrapper, core, and utility objects.

## Risks and Test Signals
Build-test on supported arches and `COMPILE_TEST`. Runtime tests are outside this file but should verify PCI probe, input device, misc devices, and vboxfs IPC consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/Makefile

## Purpose
Builds the VirtualBox guest integration module.

## APIs, Types, and Functions
Defines `vboxguest-y` as `vboxguest_linux.o`, `vboxguest_core.o`, and `vboxguest_utils.o`, then maps `CONFIG_VBOXGUEST` to `vboxguest.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
The object list combines Linux device glue, core protocol logic, and utility helpers into one module used by VirtualBox guest integration.

## Risks and Test Signals
Build-test module and built-in variants, with attention to object ordering if initialization dependencies change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/vboxguest/Makefile -->
