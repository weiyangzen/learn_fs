# subset-b-005854 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/efi.h -->
# sources/distributed-fs/ceph-client/include/linux/efi.h

Purpose: central in-kernel UEFI contract header. It defines EFI status values, GUID construction, table descriptors, memory descriptor types and attributes, runtime service function pointer ABI, system/config table layouts, capsule update structures, efivar operations, EFI device path records, secure boot helpers, TPM/random-seed/memreserve table records, and global EFI state exposed through `extern struct efi`.

Important APIs/types/functions: `efi_guid_t`, `efi_memory_desc_t`, `efi_runtime_services_t`, `efi_system_table_t`, `efi_config_table_t`, `efi_memory_map`, `efivar_operations`, `efivars`, `efi_get_secureboot_mode()`, `efi_enabled()`, `efi_rt_services_supported()`, `efi_call_virt_pointer()`, `for_each_efi_memory_desc*`, `efi_memdesc_ptr()`, efivar get/set/query helpers, capsule helpers, memreserve and MOK variable table helpers.

Control flow: architecture boot code populates `efi`, parses config tables via `efi_config_parse_tables()`, installs the memory map, optionally enters virtual mode, and routes later runtime service calls through locked/arch-wrapped helpers. Efivar users call wrapper APIs rather than firmware pointers directly. Capsule and secure boot helpers layer policy around variable/runtime operations.

State/persistence: persistent state lives in firmware variables, capsule payload/reset state, EFI memory maps, config table addresses, reserved memory tables, and secure boot/MOK data. Kernel state is mostly global and boot initialized (`efi.flags`, `efi.memmap`, table pointers, runtime_supported_mask).

Dependencies/integration: depends on architecture `asm/efi`-style call setup, `mm_struct`, kobjects/sysfs, pstore, reboot, uuid/guid, memblock/page/PFN helpers, EFI capsule loader, TPM log, Xen EFI handling, and firmware-specific runtime ABI details.

Risks/test signals: high risk around mixed 32/64-bit pointer layouts, GUID alignment, descriptor-size iteration, firmware return status mapping, runtime lock/IRQ/flag discipline, nonblocking variable store writes, and secure boot variable interpretation. Test with EFI boot/memmap parsing, efivarfs read/write/query, capsule update paths, secure boot modes, kexec/reboot, Xen EFI config tables, and malformed descriptor/table fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/efi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/efi_embedded_fw.h -->
# sources/distributed-fs/ceph-client/include/linux/efi_embedded_fw.h

Purpose: describes the EFI embedded firmware discovery interface used to locate firmware blobs baked into platform firmware and expose them by Linux firmware name.

Important APIs/types/functions: `EFI_EMBEDDED_FW_PREFIX_LEN`, private test-visible `struct efi_embedded_fw`, public match descriptor `struct efi_embedded_fw_desc`, `touchscreen_dmi_table`, and `efi_get_embedded_fw()`.

Control flow: platform-specific DMI matching supplies descriptors; EFI embedded firmware code scans firmware memory for entries matching prefix, length, and SHA256, registers found blobs, and consumers retrieve them by name through `efi_get_embedded_fw()`.

State/persistence: firmware data itself is persistent in EFI/platform firmware. Kernel runtime state is a list of discovered blobs with pointers and lengths. No file-backed persistence is introduced by this header.

Dependencies/integration: integrates DMI matching, firmware loader tests (`lib/test_firmware.c` is explicitly called out), and drivers that need fallback firmware for devices such as touchscreens.

Risks/test signals: risks are false-positive blob matches, stale SHA256/length descriptors, lifetime of firmware memory pointers, and disabled `CONFIG_EFI_EMBEDDED_FIRMWARE`. Test with DMI-matched and unmatched systems, valid/invalid hashes, duplicate names, and firmware-loader retrieval paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/efi_embedded_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/efs_vh.h -->
# sources/distributed-fs/ceph-client/include/linux/efs_vh.h

Purpose: SGI EFS volume-header on-disk structure definitions for partition and boot-file metadata.

Important APIs/types/functions: constants `VHMAGIC`, `NPARTAB`, `NVDIR`, name-size constants, `struct volume_directory`, `struct partition_table`, `struct volume_header`, partition type constants `SGI_SYSV`, `SGI_EFS`, predicate `IS_EFS()`, and `struct pt_types`.

Control flow: EFS probing code reads a 512-byte volume header, verifies `vh_magic`/checksum, scans `vh_pt[]` for `IS_EFS()` partition types, and uses `vh_vd[]` for boot/header-contained file entries.

State/persistence: all meaningful state is big-endian on-disk metadata. The header defines no mutable runtime state and no functions.

Dependencies/integration: consumed by the EFS filesystem and block/partition probing code. Uses Linux endian integer types to prevent accidental host-endian interpretation.

Risks/test signals: risks are endian conversion mistakes, assuming NUL-terminated fixed-size names, trusting partition counts or logical block numbers without bounds, and checksum mismatch handling. Test with SGI EFS images, sysv-typed EFS CD-ROM partitions, bad magic, corrupt checksum, and truncated headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/efs_vh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ehl_pse_io_aux.h -->
# sources/distributed-fs/ceph-client/include/linux/ehl_pse_io_aux.h

Purpose: small auxiliary-device contract for Intel Elkhart Lake PSE I/O subdevices.

Important APIs/types/functions: device name constants `EHL_PSE_IO_NAME`, `EHL_PSE_GPIO_NAME`, `EHL_PSE_TIO_NAME`, and `struct ehl_pse_io_data` carrying a memory resource plus IRQ.

Control flow: parent PSE I/O driver creates auxiliary devices identified by these names and passes `ehl_pse_io_data`; child drivers bind by name and consume the resource/IRQ for GPIO or PPS TIO functionality.

State/persistence: no persistent state. Runtime state is resource assignment from firmware/platform enumeration.

Dependencies/integration: depends on `struct resource` from `linux/ioport.h`, the auxiliary bus model, Intel PSE platform drivers, GPIO, and time/PPS related child drivers.

Risks/test signals: risks are mismatched child names, overlapping memory resources, invalid IRQ propagation, and ABI drift between parent and child drivers. Test auxiliary-device registration, probe/remove, resource start/size, IRQ handling, and disabled child-driver cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ehl_pse_io_aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/eisa.h -->
# sources/distributed-fs/ceph-client/include/linux/eisa.h

Purpose: defines the Linux EISA bus/device/driver interface and root-bus registration metadata.

Important APIs/types/functions: slot/resource limits, EISA register offsets, `struct eisa_device`, `struct eisa_driver`, `struct eisa_root_device`, `to_eisa_device()`, `to_eisa_driver()`, `eisa_get_region_index()`, `eisa_driver_register()`, `eisa_driver_unregister()`, driver data helpers, `eisa_root_register()`, and `EISA_bus`.

Control flow: architecture/platform code registers an EISA root with bus base/resources; the bus probes slots, creates `eisa_device` instances, and driver core matches `eisa_driver.id_table`. Without `CONFIG_EISA`, register/unregister helpers compile to no-ops.

State/persistence: hardware slot identity and resources are persistent platform state; kernel state is represented in `struct device`, resource arrays, pretty names, DMA mask, and root bus bookkeeping.

Dependencies/integration: Linux device model, ioport resources, module device tables, and legacy ISA/EISA hardware probing.

Risks/test signals: risks are incorrect I/O offset arithmetic, force-probing absent slot 0, DMA mask inheritance, resource conflicts, and no-op stubs hiding missing support. Test on EISA-capable emulation/hardware or with probe fixtures for slot signatures, resource claiming, driver binding/unbinding, and CONFIG_EISA off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/eisa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elf-fdpic.h -->
# sources/distributed-fs/ceph-client/include/linux/elf-fdpic.h

Purpose: FDPIC ELF loader state for NOMMU/MMU architectures where executable segments can be independently placed and described by a load map.

Important APIs/types/functions: ELF class aliases for `elf_fdpic_loadseg`, `elf_fdpic_loadmap`, `ELF_FDPIC_LOADMAP_VERSION`, `struct elf_fdpic_params`, arrangement flags such as `ELF_FDPIC_FLAG_HONOURVADDR`, `CONSTDISP`, `CONTIGUOUS`, stack flags, and `elf_fdpic_arch_lay_out_mm()` under MMU.

Control flow: binfmt FDPIC parses ELF headers/program headers into `elf_fdpic_params`, computes load maps for executable and interpreter, maps headers/segments/stack/dynamic areas, and optionally lets architecture layout code select addresses.

State/persistence: no persistent state; per-exec transient state holds copied headers, loadmap pointers, mapped addresses, flags, and stack requirements.

Dependencies/integration: `uapi/linux/elf-fdpic.h`, generic ELF types, binfmt loader, architecture ELF class and optional MMU layout policy.

Risks/test signals: risks are wrong ELF32/ELF64 aliases, loadmap size/version mismatch, honoring incompatible virtual addresses, stack exec/noexec policy, and interpreter/executable address collisions. Test FDPIC binaries with and without interpreters, varied PT_LOAD arrangements, PT_GNU_STACK, and MMU/NOMMU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elf-fdpic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elf-randomize.h -->
# sources/distributed-fs/ceph-client/include/linux/elf-randomize.h

Purpose: abstracts architecture support for ELF mmap and brk randomization.

Important APIs/types/functions: `arch_mmap_rnd()`, `arch_randomize_brk()`, and `compat_brk_randomized` feature macro.

Control flow: ELF binary loading asks the arch hooks for random offsets. If `CONFIG_ARCH_HAS_ELF_RANDOMIZE` is absent, mmap randomization returns zero and `arch_randomize_brk(mm)` defaults to `mm->brk` unless overridden.

State/persistence: no persistent state; randomization affects per-process virtual memory layout during exec.

Dependencies/integration: process `mm_struct`, ELF binfmt, ASLR configuration, and arch-specific overrides.

Risks/test signals: risks are silently disabling ASLR on unsupported architectures, compatibility brk behavior changes, and arch macro conflicts. Test PIE and non-PIE exec layouts, `CONFIG_COMPAT_BRK`, `randomize_va_space`, and architecture-specific brk alignment/range behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elf-randomize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elf.h -->
# sources/distributed-fs/ceph-client/include/linux/elf.h

Purpose: kernel-internal ELF compatibility layer selecting native ELF types, personality hooks, core-note extensions, and GNU property parsing hooks.

Important APIs/types/functions: default `elf_read_implies_exec()`, `SET_PERSONALITY`, `SET_PERSONALITY2`, `START_THREAD`, `ARCH_SETUP_ADDITIONAL_PAGES`, ELF32/ELF64 type aliases (`elfhdr`, `elf_phdr`, `elf_note`, `Elf_Word`), extra coredump note hooks, `struct gnu_property`, `arch_parse_elf_property()`, and `arch_elf_adjust_prot()`.

Control flow: binfmt ELF includes this header to normalize architecture callbacks; loader parses headers/properties, sets personality, maps segments, starts the new thread, and core dumping optionally emits architecture notes.

State/persistence: no own state; affects process personality, memory protections, and ELF core output generated from process state.

Dependencies/integration: `asm/elf.h`, UAPI ELF definitions, binfmt ELF, coredump code, architecture GNU property and protection policies.

Risks/test signals: risks are incorrect ELF class aliasing, defaulting read-implies-exec too broadly/narrowly, ignoring GNU properties that require protection changes, and arch coredump note size/write mismatch. Test ELF32/ELF64 exec, PT_GNU_STACK, GNU property notes, vdso/additional pages, and coredump note validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elfcore-compat.h -->
# sources/distributed-fs/ceph-client/include/linux/elfcore-compat.h

Purpose: 32-bit compatibility layouts for ELF core notes emitted by a 64-bit kernel for compat tasks.

Important APIs/types/functions: `struct compat_elf_siginfo`, `struct compat_elf_prstatus_common`, `struct compat_elf_prpsinfo`, architecture include hook `CONFIG_ARCH_HAS_ELFCORE_COMPAT`, and `struct compat_elf_prstatus`.

Control flow: compat coredump code fills these structures from task/signal/register state so user-space debuggers see the ABI-correct 32-bit core layout.

State/persistence: persistent only as generated core file contents. Runtime use is transient during coredump.

Dependencies/integration: `linux/elf.h`, native `elfcore.h`, `linux/compat.h`, architecture compat gregset definitions, signal/task coredump paths.

Risks/test signals: risks are layout drift from native definitions, hard-coded `pr_fname[16]` ABI, wrong compat time/pid/uid sizes, and missing arch compat register definitions. Test compat process coredumps, gdb/readelf decoding, register note sizes, and mixed 32-bit userspace on 64-bit kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elfcore-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elfcore.h -->
# sources/distributed-fs/ceph-client/include/linux/elfcore.h

Purpose: native ELF core file process/status note definitions and helper hooks for dumping register and architecture-specific extra core segments.

Important APIs/types/functions: `struct elf_siginfo`, `struct elf_prstatus_common`, `struct elf_prstatus`, `ELF_PRARGSZ`, `struct elf_prpsinfo`, `elf_core_copy_regs()`, `elf_core_copy_task_regs()`, `elf_core_copy_task_fpregs()`, and optional extra PHDR/data hooks.

Control flow: core dump generation copies signal/process metadata and register sets into ELF notes, optionally adding gate/vDSO or architecture-specific program headers/data.

State/persistence: generated ELF core file persists task state snapshots; no kernel-persistent state is declared.

Dependencies/integration: task stack/ptrace/user register types, `asm/elf.h` macros, `fs/binfmt_elf.c`, coredump params, architecture FPU and extra-PHDR implementations.

Risks/test signals: risks are register-set size mismatch, `BUG_ON` fallback on incompatible layouts, stale hard-coded task name length, and extra PHDR size/write inconsistency. Test native coredumps, FPU-heavy tasks, arch extra note/segment support, and debugger consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elfcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elfnote-lto.h -->
# sources/distributed-fs/ceph-client/include/linux/elfnote-lto.h

Purpose: emits a Linux ELF note indicating whether the kernel was built with LTO.

Important APIs/types/functions: `LINUX_ELFNOTE_LTO_INFO` and `BUILD_LTO_INFO`, which expands to an `ELFNOTE32("Linux", ..., 1|0)` depending on `CONFIG_LTO`.

Control flow: build/assembly code includes the macro to place a note in the kernel image; external tools can inspect the PT_NOTE data.

State/persistence: build metadata persists in the linked ELF image. No runtime state.

Dependencies/integration: `linux/elfnote.h`, linker note sections, `CONFIG_LTO`, and tooling reading vmlinux notes.

Risks/test signals: risks are missing note emission in build paths, wrong value under mixed LTO configs, and section alignment issues inherited from elfnote macros. Test with LTO on/off builds and `readelf -n` validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elfnote-lto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elfnote.h -->
# sources/distributed-fs/ceph-client/include/linux/elfnote.h

Purpose: macro framework for generating ELF notes from C or assembly into `.note.NAME` sections later packed into PT_NOTE.

Important APIs/types/functions: assembler note macros and C macros such as `ELFNOTE_START`, `ELFNOTE_END`, `ELFNOTE`, and `ELFNOTE32`/typed variants, with alignment and name/desc sizing logic.

Control flow: build-time code expands macros into note header/name/description records. The linker coalesces note sections into kernel image notes for bootloaders or external tools.

State/persistence: metadata persists in the ELF binary, not in runtime kernel memory as a managed subsystem.

Dependencies/integration: assembler syntax, linker section handling, ELF note ABI, vmlinux/module build metadata, and headers such as `elfnote-lto.h`.

Risks/test signals: risks are alignment errors, assembler/C macro divergence, malformed name sizes, missing terminating NUL for note names, and toolchain section syntax differences. Test by compiling C and assembly users and checking `readelf -n` note parseability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/elfnote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/enclosure.h -->
# sources/distributed-fs/ceph-client/include/linux/enclosure.h

Purpose: generic enclosure services API for storage chassis slots/components.

Important APIs/types/functions: enclosure/component enums for status, type, control, and power-cycle policy; `struct enclosure_component_callbacks`; `struct enclosure_component`; `struct enclosure_device`; registration helpers such as `enclosure_register()`, `enclosure_unregister()`, `enclosure_component_register()`, `enclosure_find()`, and device accessors.

Control flow: storage or SES-like drivers register an enclosure device with callbacks, register individual components/slots, and the enclosure class exposes status/control through device model/sysfs. Callbacks mediate get/set of fault, status, locate, power, and active indicators.

State/persistence: runtime component state is cached in `enclosure_component` and reflected to hardware through callbacks. Persistent physical state belongs to enclosure hardware and may survive reboot independently.

Dependencies/integration: Linux device model, storage stack, SCSI enclosure services, sysfs class devices, and driver callbacks.

Risks/test signals: risks are stale cached slot state, incorrect component numbering, unsupported callback handling, lifetime/refcount bugs between enclosure and component devices, and hardware state races. Test register/unregister, sysfs reads/writes, fault/locate toggles, component lookup, and hot-remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/enclosure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/energy_model.h -->
# sources/distributed-fs/ceph-client/include/linux/energy_model.h

Purpose: scheduler/device energy model interface describing performance states, power/cost tables, and CPU performance domains used by Energy Aware Scheduling and device power estimation.

Important APIs/types/functions: `struct em_perf_state`, `struct em_perf_table`, `struct em_perf_domain`, flags `EM_PERF_STATE_INEFFICIENT`, `EM_PERF_DOMAIN_*`, callback `struct em_data_callback`, registration/update helpers, `em_cpu_get()`, `em_pd_get()`, `em_table_alloc/free()`, `em_cpu_energy()`, `em_pd_get_efficient_state()`, `em_perf_state_from_pd()`, and disabled stubs when `CONFIG_ENERGY_MODEL` is off.

Control flow: a CPU/device provider registers a performance domain with callbacks; EM code builds cost tables and updates them under RCU/kref. Scheduler hot paths read tables under RCU and compute energy by mapping utilization to an efficient performance state and multiplying `ps->cost * sum_util`.

State/persistence: runtime state includes RCU-protected performance tables, per-domain cpumasks, limits, flags, and kobjects. No disk persistence; data may reflect firmware/DT/driver power tables.

Dependencies/integration: cpumasks, device model, scheduler topology/cpufreq, jump labels, RCU, krefs, thermal/capacity limits.

Risks/test signals: risks are overflow on 32-bit platforms, stale RCU table access, incorrect inefficient-state filtering, mismatched cpumasks/CPUFreq policies, and invalid power/frequency monotonicity. Test EM registration, EAS scheduling decisions, hotplug, table updates, chip binning, disabled config stubs, and lockdep RCU assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/energy_model.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/entry-common.h -->
# sources/distributed-fs/ceph-client/include/linux/entry-common.h

Purpose: generic syscall entry/exit work orchestration shared by architectures.

Important APIs/types/functions: `SYSCALL_WORK_ENTER`, `SYSCALL_WORK_EXIT`, arch override wrappers for ptrace entry/exit, `syscall_user_dispatch()`, trace hooks, `syscall_enter_audit()`, `syscall_trace_enter()`, `syscall_enter_from_user_mode_work()`, `syscall_enter_from_user_mode()`, `report_single_step()`, `syscall_exit_work()`, `syscall_exit_to_user_mode_work()`, and `syscall_exit_to_user_mode()`.

Control flow: architecture code enters from user mode, enables instrumentation/IRQs at defined points, handles syscall user dispatch first, rseq slice work, ptrace, seccomp, tracepoints, audit, and then executes or skips the syscall. Exit handles rseq return, audit, tracepoints, ptrace/singlestep, disables IRQs, processes return-to-user work, and finalizes context tracking.

State/persistence: uses per-thread `syscall_work`, current task audit/seccomp/rseq/dispatch state, and pt_regs. No persistent state beyond task flags.

Dependencies/integration: audit, ptrace, seccomp, rseq, livepatch/user-mode resume, IRQ/context tracking, arch syscall accessors, tracepoints.

Risks/test signals: risks are wrong ordering of dispatch/ptrace/seccomp, IRQ state leaks, instrumentation in non-instrumentable regions, skipped syscall return semantics, and single-step handling. Test tracing, seccomp, ptrace SYSEMU, syscall user dispatch, audit, rseq, lockdep IRQ warnings, and architecture entry selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/entry-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/entry-virt.h -->
# sources/distributed-fs/ceph-client/include/linux/entry-virt.h

Purpose: virtual-machine guest-entry preparation hooks for handling work before transferring from host kernel context to guest mode.

Important APIs/types/functions: `XFER_TO_GUEST_MODE_WORK`, `arch_xfer_to_guest_mode_handle_work()`, `xfer_to_guest_mode_handle_work()`, `xfer_to_guest_mode_prepare()`, `__xfer_to_guest_mode_work_pending()`, and `xfer_to_guest_mode_work_pending()`.

Control flow: virtualization code checks pending thread work relevant to guest entry, repeatedly handles architecture/common work until clear, then proceeds to guest. When `CONFIG_VIRT_XFER_TO_GUEST_WORK` is absent, the interface is not active.

State/persistence: uses current thread-info flags/work bits. No persistent state.

Dependencies/integration: KVM/virtualization entry paths, architecture-defined guest-entry work bits, IRQ/preemption/context tracking constraints.

Risks/test signals: risks are entering guest with unhandled signals/resched/arch work, infinite retry if work is not cleared, or missing arch macro definitions when config is enabled. Test KVM run loops, signal delivery while entering guest, resched/IPI races, and architecture-specific guest-entry work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/entry-virt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/err.h -->
# sources/distributed-fs/ceph-client/include/linux/err.h

Purpose: standard kernel error-pointer encoding helpers.

Important APIs/types/functions: `MAX_ERRNO`, `IS_ERR_VALUE()`, `ERR_PTR()`, `INIT_ERR_PTR()`, `ERR_PTR_PCPU()`, `IOMEM_ERR_PTR()`, `PTR_ERR()`, `PTR_ERR_PCPU()`, `IS_ERR()`, `IS_ERR_PCPU()`, `IS_ERR_OR_NULL()`, `ERR_CAST()`, `PTR_ERR_OR_ZERO()`.

Control flow: APIs that normally return pointers encode negative errno values in the high invalid pointer range; callers test with `IS_ERR*()` and recover errno with `PTR_ERR()`.

State/persistence: no state. Encoded values are transient return values.

Dependencies/integration: sparse address-space annotations (`__iomem`, `__percpu`), compiler `__must_check`, branch prediction, and broad kernel pointer-return conventions.

Risks/test signals: risks are dereferencing encoded errors, mixing NULL and ERR_PTR semantics, losing address-space qualifiers, and returning positive values through `ERR_PTR`. Test call sites with allocation/probe failures, sparse warnings, and static analysis for missing `IS_ERR` checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/errname.h -->
# sources/distributed-fs/ceph-client/include/linux/errname.h

Purpose: optional symbolic errno-name lookup.

Important APIs/types/functions: `errname(int err)`, returning a symbolic name when `CONFIG_SYMBOLIC_ERRNAME` is enabled, otherwise returning `NULL`.

Control flow: diagnostic code can call `errname()` and fall back to numeric formatting if it returns NULL.

State/persistence: no state.

Dependencies/integration: errno tables compiled under `CONFIG_SYMBOLIC_ERRNAME`, logging and debug paths.

Risks/test signals: risks are assuming non-NULL names when config is off or passing positive/non-errno values. Test logging with config on/off and representative negative errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/errname.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/errno.h -->
# sources/distributed-fs/ceph-client/include/linux/errno.h

Purpose: internal kernel errno extensions beyond UAPI errno values.

Important APIs/types/functions: restart/internal codes `ERESTARTSYS`, `ERESTARTNOINTR`, `ERESTARTNOHAND`, `ERESTART_RESTARTBLOCK`, probe/open/ioctl codes such as `ENOIOCTLCMD`, `EPROBE_DEFER`, `EOPENSTALE`, `ENOPARAM`, NFS/internal network filesystem codes, `EIOCBQUEUED`, `ERECALLCONFLICT`, and `ENOGRACE`.

Control flow: syscalls and subsystems return these internal negative errors; VFS/syscall exit, signal restart logic, driver core, NFS, and AIO convert or consume them before exposing user-visible errno.

State/persistence: no state; values are ABI-sensitive internal constants.

Dependencies/integration: UAPI asm errno, syscall restart machinery, driver probing, NFS/exportfs, VFS open, async I/O.

Risks/test signals: risks are leaking internal restart codes to userspace, numeric collisions, and mishandling `EPROBE_DEFER` or queued AIO. Test syscall interruption/restart, deferred probe, stale open retry, NFS error translation, and ioctl unknown-command paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/error-injection.h -->
# sources/distributed-fs/ceph-client/include/linux/error-injection.h

Purpose: function error-injection eligibility API.

Important APIs/types/functions: `within_error_injection_list()` and `get_injectable_error_type()`, with disabled stubs returning false/zero when `CONFIG_FUNCTION_ERROR_INJECTION` is off.

Control flow: tracing/fault-injection infrastructure checks whether a function address is injectable and what error type is legal before forcing a failure.

State/persistence: injectable function metadata is build/runtime registration state outside this header; no persistence here.

Dependencies/integration: ftrace/kprobes/error-injection infrastructure, annotated functions, and fault-injection tests.

Risks/test signals: risks are injecting into unsafe functions, wrong return type classification, or stubs masking tests when config is off. Test with annotated injectable functions, invalid addresses, config-off builds, and fault-injection selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/error-injection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/errqueue.h -->
# sources/distributed-fs/ceph-client/include/linux/errqueue.h

Purpose: socket error-queue control block overlay for extended asynchronous errors.

Important APIs/types/functions: `SKB_EXT_ERR(skb)` and `struct sock_exterr_skb`, containing `sock_extended_err`, optional IPv6 address, original payload offset, and port.

Control flow: networking code records ICMP/PMTU/timestamping or protocol errors in skb control buffer; socket error queue consumers cast through `SKB_EXT_ERR()` to read metadata.

State/persistence: transient skb control block state until delivered/read from the socket error queue.

Dependencies/integration: `uapi/linux/errqueue.h`, skb `cb`, IPv6 config, socket error queues, ICMP/IPV6 and timestamping paths.

Risks/test signals: risks are skb control-buffer layout conflicts, missing IPv6 address field under config changes, stale origin/port values, and overrun of `skb->cb`. Test `IP_RECVERR`, IPv6 receive errors, PMTU discovery, timestamping error queue delivery, and cb-size assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/errqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/errseq.h -->
# sources/distributed-fs/ceph-client/include/linux/errseq.h

Purpose: compact sequence/error tracking type used to report writeback and other delayed errors once per observer.

Important APIs/types/functions: `typedef u32 errseq_t`, `errseq_set()`, `errseq_check()`, and `errseq_check_and_advance()`.

Control flow: producers update an `errseq_t` when an error occurs; consumers snapshot a prior value and later check or advance their cursor to detect new errors without repeatedly reporting old ones.

State/persistence: the sequence word is stored in owning kernel objects such as superblocks/files and persists for their lifetime, not across reboot.

Dependencies/integration: writeback error reporting, file `fsync`/`close`, superblock error state.

Risks/test signals: risks are lost errors due to wrap/incorrect cursor updates, reporting stale errors to new observers, and data races if used outside intended atomic implementation. Test delayed writeback errors, multiple file descriptors with different cursors, repeated fsync, and error overwrite ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/errseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/etherdevice.h -->
# sources/distributed-fs/ceph-client/include/linux/etherdevice.h

Purpose: Ethernet netdevice allocation, header handling, MAC address utilities, and packet helper API.

Important APIs/types/functions: platform MAC retrieval helpers, Ethernet header ops, `alloc_etherdev*`, `devm_alloc_etherdev*`, GRO helpers, reserved multicast bases, address predicates (`is_zero_ether_addr`, `is_multicast_ether_addr`, `is_valid_ether_addr`), address mutators/copy/equality helpers, `compare_ether_header()`, `eth_hw_addr_gen()`, `eth_skb_pkt_type()`, `eth_skb_pull_mac()`, and `eth_skb_pad()`.

Control flow: drivers allocate Ethernet devices, set or discover MAC addresses, validate/change addresses through standard helpers, parse/build Ethernet headers, and classify inbound skb packet type before upper-layer delivery.

State/persistence: netdevice MAC address and assignment type are runtime device state; platform/NVMEM firmware may persist hardware addresses. skb helpers mutate packet metadata/data pointers.

Dependencies/integration: `net_device`, skb, neighbour/header cache, random, CRC32, unaligned access capabilities, endian/BITS_PER_LONG optimizations, firmware nodes/NVMEM.

Risks/test signals: risks are alignment-sensitive fast paths, endian-specific multicast tests, invalid random/generated MACs, skb underrun/padding failures, and RCU address-list iteration. Test unaligned and aligned architectures, MAC validation, multicast/broadcast classification, NVMEM/platform MAC retrieval, GRO, and packet type assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/etherdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ethtool.h -->
# sources/distributed-fs/ceph-client/include/linux/ethtool.h

Purpose: in-kernel ethtool driver API for link settings, RSS, rings, coalescing, statistics, module EEPROM/power, timestamping, FEC/RMON, MAC Merge, PHY operations, and generic helpers.

Important APIs/types/functions: `struct ethtool_ops`, `struct ethtool_phy_ops`, RSS context/parameter structures, `ethtool_link_ksettings`, link mode bitmap macros, coalesce capability masks, many standardized stats structures, MAC Merge state/config/stats and software verification helpers, `kernel_ethtool_ts_info`, `ethtool_check_ops()`, RX flow rule helpers, virtual-device helpers, per-netdev ethtool state, `ethtool_op_get_link()`, `ethtool_op_get_ts_info()`, string helpers, and forced-speed maps.

Control flow: ethtool ioctl/netlink core validates requests, takes RTNL, calls optional driver callbacks, aggregates or initializes standardized stats, manages RSS contexts in per-netdev state, and handles MAC Merge verification through timer/event helpers.

State/persistence: driver/device settings include link modes, RSS tables/keys/contexts, WOL, coalescing, rings, module power, timestamping, and MAC Merge state. Most is hardware/runtime state; some devices persist firmware/module settings.

Dependencies/integration: UAPI ethtool/netlink, netdev, PHY library, netlink extack, timers, xarray, PTP/hwtstamp, flow rules, module EEPROM, IEEE stats.

Risks/test signals: risks are optional callback NULL handling, incorrect supported_* masks, RSS context lifetime/resizing, stats fields not initialized to `ETHTOOL_STAT_NOT_SET`, RTNL/locking violations, and MAC Merge timer races. Test ioctl and netlink paths, driver callback validation, RSS create/modify/delete, stats omission, module EEPROM page access, PHC timestamping, FEC/RMON, and MAC Merge state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ethtool_netlink.h -->
# sources/distributed-fs/ceph-client/include/linux/ethtool_netlink.h

Purpose: kernel helpers for ethtool generic-netlink integration, especially cable-test event reporting and aggregate stats.

Important APIs/types/functions: link-mode mask word count, pause stat count, multicast group enum, cable test allocation/result/fault/amplitude/pulse/step helpers, aggregate MAC/PHY/control/pause/RMON stat helpers, `ethtool_dev_mm_supported()`, `ethnl_pse_send_ntf()`, and disabled stubs.

Control flow: PHY drivers start a cable test, allocate netlink state, emit result/fault/step events, and signal finish. Etntool netlink code aggregates stats from device callbacks for user replies. Without `CONFIG_ETHTOOL_NETLINK`, helpers return `-EOPNOTSUPP` or no-op.

State/persistence: transient cable-test state and netlink notifications; aggregate stats are snapshots.

Dependencies/integration: generic netlink family, PHY devices, netdev ethtool ops, UAPI ethtool netlink generated constants, PSE notifications.

Risks/test signals: risks are emitting events without allocation, config-off behavior, source-index mismatches in cable pairs, and stats aggregation double-counting. Test cable test lifecycle, netlink multicast listeners, config-off callers, MAC Merge support reporting, and stat aggregation with partial driver callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ethtool_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/eventfd.h -->
# sources/distributed-fs/ceph-client/include/linux/eventfd.h

Purpose: kernel API for eventfd counters used as lightweight notification objects.

Important APIs/types/functions: flag masks `EFD_SHARED_FCNTL_FLAGS`, `EFD_FLAGS_SET`, opaque `eventfd_ctx`, `eventfd_ctx_put()`, fd/file getters, `eventfd_signal_mask()`, `eventfd_ctx_remove_wait_queue()`, `eventfd_ctx_do_read()`, `eventfd_signal_allowed()`, and `eventfd_signal()`.

Control flow: subsystems obtain an eventfd context from fd/file, signal it with optional poll mask when an event occurs, optionally remove wait queues/read counters, and release references. Disabled config stubs return errors/no-op.

State/persistence: eventfd counter and wait queue live in `eventfd_ctx` and persist while referenced/open. No disk persistence.

Dependencies/integration: file descriptors, poll masks, wait queues, scheduler/task context constraints, KVM/aio/io_uring/user notification users.

Risks/test signals: risks are signaling from disallowed contexts, reference leaks, counter saturation semantics, missing wakeups, and config-off handling. Test fdget/fileget, signal/read behavior, semaphore mode, poll wakeups, wait queue removal, and users such as KVM irqfd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/eventfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/eventpoll.h -->
# sources/distributed-fs/ceph-client/include/linux/eventpoll.h

Purpose: internal epoll hooks for file release, event delivery, control operations, and ARM OABI event translation.

Important APIs/types/functions: `eventpoll_release_file()`, `eventpoll_release()`, `epoll_sendevents()`, `do_epoll_ctl()`, `ep_op_has_event()`, optional `get_epoll_tfile_raw_ptr()` for KCMP, and `ep_take_care_of_epollwakeup()` for ARM OABI compat handling.

Control flow: file close/release calls `eventpoll_release()` to detach watched files; syscalls use `do_epoll_ctl()` and `epoll_sendevents()`; operation validation checks whether an op includes an event payload.

State/persistence: epoll interest lists and ready lists live in epoll file state. No persistence beyond file lifetime.

Dependencies/integration: `CONFIG_EPOLL`, file/VFS lifecycle, user-copy of `struct epoll_event`, KCMP, ARM OABI compatibility.

Risks/test signals: risks are dangling watched-file references on close, wrong op validation, user event copy/compat translation errors, and config-off callers. Test epoll_ctl add/mod/del, concurrent close, nested epoll, KCMP inspection, ARM OABI compat, and disabled config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/eventpoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/evm.h -->
# sources/distributed-fs/ceph-client/include/linux/evm.h

Purpose: Extended Verification Module interface for protecting and validating file metadata/xattrs.

Important APIs/types/functions: `evm_set_key()`, `evm_verifyxattr()`, `evm_fix_hmac()`, `evm_inode_init_security()`, `evm_revalidate_status()`, `evm_protected_xattr_if_enabled()`, `evm_read_protected_xattrs()`, `evm_metadata_changed()`, and `posix_xattr_acl()` helper/stub.

Control flow: LSM/integrity and filesystem paths call EVM when setting security xattrs, verifying protected xattrs, initializing inode security, or detecting metadata changes. Disabled stubs allow callers to compile while returning permissive or unsupported results.

State/persistence: EVM HMAC/signature values are stored in protected xattrs on files; key material is runtime kernel state.

Dependencies/integration: integrity subsystem, IMA/EVM, dentries/inodes, xattrs, POSIX ACLs, LSM security initialization.

Risks/test signals: risks are accepting stale metadata after protected xattr changes, disabled-config semantic differences, key setup failures, and ACL xattr classification errors. Test xattr verification/fixup, metadata mutation, key loading, fs with/without ACLs, IMA/EVM policy, and config-off behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/evm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/execmem.h -->
# sources/distributed-fs/ceph-client/include/linux/execmem.h

Purpose: architecture-parameterized executable memory allocator for modules, kprobes, ftrace, BPF, and module data.

Important APIs/types/functions: `MODULE_ALIGN`, `enum execmem_type`, `enum execmem_range_flags`, ROX hooks `execmem_fill_trapping_insns()` and `execmem_restore_rox()`, `struct execmem_range`, `struct execmem_info`, `execmem_arch_setup()`, `execmem_alloc()`, `execmem_alloc_rw()`, `execmem_free()`, cleanup helper, `execmem_vmap()`, `execmem_is_rox()`, and `execmem_init()`.

Control flow: early init obtains arch ranges/defaults; subsystems allocate executable memory by type; architectures may enforce placement, permissions, alignment, KASAN shadow, and ROX cache. Callers using writable allocations must restore/manage permissions.

State/persistence: runtime allocator state and virtual mappings; no disk persistence. Allocated code/data remains until freed or module/subsystem teardown.

Dependencies/integration: module loader, vmalloc/vmap, KASAN, architecture text permissions, BPF JIT, ftrace, kprobes, cleanup annotations.

Risks/test signals: risks are W+X exposure, wrong executable range for branch reachability, KASAN shadow gaps, ROX restoration failure, alignment mistakes, and late init ordering. Test module load/unload, BPF JIT allocation, kprobe/ftrace text allocation, strict W^X/debug page permissions, KASAN configs, and arch fallback ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/execmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/export-internal.h -->
# sources/distributed-fs/ceph-client/include/linux/export-internal.h

Purpose: internal macros for modpost-generated C files to emit kernel symbol table, CRC, and flag records.

Important APIs/types/functions: relocation-aware `__KSYM_ALIGN`, `__KSYM_REF()`, `__KSYMTAB()`, `KSYM_FUNC()`, `KSYMTAB_FUNC()`, `KSYMTAB_DATA()`, `SYMBOL_CRC()`, and `SYMBOL_FLAGS()`.

Control flow: generated files expand these macros into inline assembly sections: symbol/name/namespace strings, `___ksymtab+name` entries, `___kcrctab+sym` CRCs, and `___kflagstab+sym` flags. PREL32 relocations are used when supported to reduce relocations/size.

State/persistence: export metadata persists in the linked kernel/module image and is used by module loader/modpost.

Dependencies/integration: modpost, linker sections, module loader, genksyms/versioning, architecture relocation support, parisc function descriptors.

Risks/test signals: risks are section syntax incompatibility, wrong relative relocation computation, namespace string mismatch, CRC endian/size issues, and direct inclusion by normal code. Test module symbol resolution, modversions, namespace imports, PREL32 and non-PREL32 architectures, and `readelf` section contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/export-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/export.h -->
# sources/distributed-fs/ceph-client/include/linux/export.h

Purpose: public source-level macros for exporting kernel symbols to modules.

Important APIs/types/functions: `EXPORT_SYMBOL()`, `EXPORT_SYMBOL_GPL()`, namespace variants, `EXPORT_SYMBOL_FOR_MODULES()`, and internal `__EXPORT_SYMBOL()` variants for assembly, genksyms, GENDWARFKSYMS, and disabled exports.

Control flow: C or assembly files annotate symbols; build macros emit `.export_symbol` records with license, namespace, and symbol reference, or genksyms metadata during symbol version generation. Runtime module loading uses the resulting export tables.

State/persistence: export records persist in kernel/module ELF sections. No runtime mutable state in this header.

Dependencies/integration: compiler addressability, linkage/stringify helpers, genksyms/gendwarfksyms, module loader, namespace enforcement, fixdep rebuild behavior on modversion changes.

Risks/test signals: risks are exporting unintended symbols, namespace/license mismatches, dead-code elimination without `__ADDRESSABLE`, assembly string literal issues, and disabled exports in special build contexts. Test module builds, GPL-only enforcement, namespace import warnings/errors, modversions toggles, and LLVM/GAS assembly handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/exportfs.h -->
# sources/distributed-fs/ceph-client/include/linux/exportfs.h

Purpose: VFS/NFS file-handle encoding and decoding contract for exportable filesystems and `open_by_handle_at()`.

Important APIs/types/functions: `MAX_HANDLE_SZ`, `enum fid_type`, `struct fid`, handle flags, user flags, `struct handle_to_path_ctx`, `struct export_operations`, export operation flags, `exportfs_cannot_lock()`, `exportfs_encode_inode_fh()`, `exportfs_encode_fh()`, capability predicates, `exportfs_encode_fid()`, `exportfs_decode_fh_raw()`, `exportfs_decode_fh()`, and generic inode-number helpers.

Control flow: filesystems implement export ops to encode inode/parent identity and decode handles to dentries. NFSd and handle syscalls validate capabilities, encode connectable or non-decodeable FIDs, decode raw handles, check permissions/subtree constraints, and use filesystem metadata commit/block layout callbacks when provided.

State/persistence: file handles encode persistent filesystem object identity such as inode/generation/subvolume/checkpoint. Runtime state includes dentries/inodes and export op flags.

Dependencies/integration: VFS dentries/inodes/superblocks, NFSd, open-by-handle syscalls, iomap/block layout, filesystem-specific stable identifiers.

Risks/test signals: risks are stale or forgeable handles, missing parent info for subtree checks, custom open/permission ops not respected by NFSd, wrong fid length units, and generation reuse. Test NFS export, `name_to_handle_at`/`open_by_handle_at`, stale inode generation, connectable handles, directory-only decode, and generic helpers on filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/exportfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ext2_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/ext2_fs.h

Purpose: small ext2 on-disk constants and image-size helper.

Important APIs/types/functions: `EXT2_NAME_LEN`, `EXT2_LINK_MAX`, superblock offsets `EXT2_SB_MAGIC_OFFSET`, `EXT2_SB_BLOCKS_OFFSET`, `EXT2_SB_BSIZE_OFFSET`, and `ext2_image_size()`.

Control flow: `ext2_image_size()` treats the provided buffer as an ext2 superblock, verifies magic at offset `0x38`, then computes total bytes from block count shifted by block-size log.

State/persistence: reads persistent ext2 superblock fields. No runtime state.

Dependencies/integration: ext2/ext-family image probing, `linux/magic.h`, endian conversion helpers.

Risks/test signals: risks are unaligned superblock buffer access, trusting too-small buffers, overflow/invalid block-size values, and confusing ext2-compatible metadata with other filesystems. Test valid ext2 images, bad magic, large block counts, malformed block-size log, and unaligned buffers on strict architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ext2_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/extable.h -->
# sources/distributed-fs/ceph-client/include/linux/extable.h

Purpose: exception table search/sort API for recovering from faulting kernel instruction ranges.

Important APIs/types/functions: `search_extable()`, `sort_extable()`, `sort_main_extable()`, `trim_init_extable()`, `search_exception_tables()`, `search_kernel_exception_table()`, optional `search_module_extables()`, and optional `search_bpf_extables()`.

Control flow: boot/module load sorts exception tables; fault handlers call search helpers by instruction address; module and BPF JIT tables are included conditionally; init tables can be trimmed after init.

State/persistence: exception table entries are linked into kernel/modules/BPF JIT metadata and persist for code lifetime.

Dependencies/integration: architecture exception table entry format, modules, BPF JIT, fault handlers, linker sections.

Risks/test signals: risks are unsorted tables causing failed lookup, stale module/BPF entries after unload, trimming too aggressively, and address comparison bugs. Test uaccess fault fixups, module load/unload exception fixups, BPF JIT fault recovery, and boot-time sort validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/extcon-provider.h -->
# sources/distributed-fs/ceph-client/include/linux/extcon-provider.h

Purpose: provider-side API for registering external connector devices and publishing connector state/property changes.

Important APIs/types/functions: `extcon_dev_register/unregister`, devm registration, allocation/free helpers, `extcon_sync()`, `extcon_set_state()`, `extcon_set_state_sync()`, `extcon_set_property()`, `extcon_set_property_sync()`, and `extcon_set_property_capability()` plus disabled stubs.

Control flow: provider drivers allocate an `extcon_dev`, register it, declare property capabilities, update connector state/properties, and sync notifications to consumers. Managed variants tie lifetime to a device.

State/persistence: runtime extcon state/properties and notifier state in `extcon_dev`; physical connector state is hardware-derived and may persist electrically but is re-detected.

Dependencies/integration: extcon core, device model/devres, notifier chains, consumer API in `extcon.h`, charger/USB/display/jack drivers.

Risks/test signals: risks are setting unsupported properties, missed sync notifications, managed/unmanaged lifetime mixups, and config-off stubs returning success for state updates. Test provider probe/remove, state/property notifications, devm cleanup, unsupported ID/property errors, and disabled config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/extcon-provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/extcon.h -->
# sources/distributed-fs/ceph-client/include/linux/extcon.h

Purpose: consumer-facing external connector ID/property definitions and notifier lookup API.

Important APIs/types/functions: connector type/id constants for USB, chargers, jacks, displays, misc connectors; property constants/ranges; `union extcon_property_value`; `extcon_get_state()`, property get/capability helpers, per-ID and all-connector notifier registration/devm variants, lookup helpers by name/device tree phandle, `extcon_get_edev_name()`, and deprecated `struct extcon_specific_cable_nb`.

Control flow: consumers obtain an `extcon_dev`, query current state/properties, and register notifiers for connector changes. Provider updates are delivered through extcon core. Config-off stubs return neutral values or errors depending on lookup/managed operation.

State/persistence: runtime connector state/properties and notifier registrations. No disk persistence.

Dependencies/integration: device model, device tree nodes/phandles, notifier blocks, USB/charger/audio/display drivers, provider API.

Risks/test signals: risks are ID/property range drift, ambiguous config-off success stubs, notifier leaks, phandle lookup failures, and deprecated API users. Test connector state changes, property capabilities, all-vs-specific notifiers, DT lookup, devm unregister, and type/range validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/extcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/extcon/extcon-adc-jack.h -->
# sources/distributed-fs/ceph-client/include/linux/extcon/extcon-adc-jack.h

Purpose: platform-data contract for an ADC-based analog jack extcon provider.

Important APIs/types/functions: `struct adc_jack_cond` mapping connector ID to inclusive ADC range, and `struct adc_jack_pdata` carrying extcon name, IIO consumer channel name, supported cable IDs, ADC conditions, IRQ flags, debounce/handling delay, and wakeup-source flag.

Control flow: the ADC jack driver receives platform data, waits for IRQ, optionally delays, samples the ADC channel, selects the first matching condition, and publishes extcon state; no match means no cable attached.

State/persistence: runtime sampled ADC-derived connector state. Hardware accessory connection may persist physically; kernel state is recalculated.

Dependencies/integration: extcon core, module/platform data, IIO ADC consumer channel, IRQ handling, wakeup source integration.

Risks/test signals: risks are overlapping ADC ranges, missing sentinel condition, delay rounding, noisy ADC readings, incorrect cable ID list, and wakeup misconfiguration. Test boundary ADC values, no-match state clearing, IRQ debounce, suspend wakeup, and multiple cable conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/extcon/extcon-adc-jack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/f2fs_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/f2fs_fs.h

Purpose: F2FS on-disk format definitions shared by kernel code and tooling-like users: superblock, checkpoint, NAT/SIT, node, summary, journal, and directory-entry layouts.

Important APIs/types/functions: block/segment constants, sentinel block addresses, inode-number macros, stop-checkpoint and corruption enums, `struct f2fs_super_block`, checkpoint flags and `struct f2fs_checkpoint`, orphan blocks, node/inode/direct/indirect layouts, NAT/SIT structures and macros, summary/journal structures, dentry hash/slot constants, `struct f2fs_dir_entry`, and `struct f2fs_dentry_block`.

Control flow: mount/recovery code reads superblock and checkpoint packs, validates flags/checksums, reconstructs orphan/NAT/SIT/summary state, and interprets node/dentry blocks through these packed little-endian structures. Runtime allocation and recovery update persistent checkpoint, segment, NAT/SIT, and journal metadata.

State/persistence: nearly every structure here is persistent on-disk metadata. It tracks filesystem geometry, feature flags, checkpoint versions, valid block/inode counts, current segments, orphan inode lists, inode inline/compression attributes, NAT node-to-block mappings, SIT segment validity/age, and directory entries.

Dependencies/integration: page/block size assumptions, endian helpers, F2FS core mount/recovery/GC/directory code, compression, quota, encryption, project IDs, fsck compatibility.

Risks/test signals: risks are packed layout drift, page-size dependent geometry, endian mistakes, feature/checkpoint flag misinterpretation, flexible/zero-length placeholder misuse, corruption reason array bounds, and malformed directory slots. Test mount/fsck of varied F2FS images, crash recovery, orphan handling, compression/inline xattrs, NAT/SIT journal replay, large page sizes, and corrupt metadata fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/f2fs_fs.h -->
