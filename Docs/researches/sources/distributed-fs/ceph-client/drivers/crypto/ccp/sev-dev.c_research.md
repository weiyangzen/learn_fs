# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev.c

## Purpose

`sev-dev.c` implements the AMD Secure Encrypted Virtualization and SEV-SNP PSP firmware interface. It registers `/dev/sev`, exposes platform ioctls, submits SEV/SNP/TIO firmware commands, manages SEV/SNP platform initialization and shutdown, handles SNP firmware-owned page transitions, maintains persistent INIT_EX storage, and exports helper APIs to KVM and other kernel users.

## Important APIs, Types, And Functions

External APIs include `sev_dev_init()`, `sev_dev_destroy()`, `sev_platform_init()`, `sev_platform_shutdown()`, `sev_do_cmd()`, `__sev_do_cmd_locked()`, SEV guest helpers, `snp_alloc_firmware_page()`, `snp_free_firmware_page()`, `snp_alloc_hv_fixed_pages()`, `snp_free_hv_fixed_pages()`, `sev_get_snp_policy_bits()`, and `sev_issue_cmd_external_user()`. Major internal areas are command buffer sizing, INIT/INIT_EX/NV file handling, SNP platform data and feature discovery, RMP firmware-page helpers, legacy SEV command bounce descriptors, ioctl handlers, firmware update, panic shutdown, and TIO initialization.

## Control Flow

`sev_dev_init()` validates CPU SEV support, allocates a two-page command buffer, registers the SEV IRQ callback, and creates `/dev/sev`. PCI init obtains firmware API/version state and optionally downloads firmware. `sev_platform_init()` serializes on `sev_cmd_mutex`, initializes SNP first when supported, then legacy SEV unless deferred. SNP init builds an optional reserved-memory/HV-fixed range list, prepares RMP state, executes `SNP_INIT[_EX]`, flushes caches, runs `SNP_DF_FLUSH`, registers panic shutdown, and may initialize SEV-TIO. Command submission copies caller data into a physical scratch command buffer, prepares SNP legacy buffer state when needed, writes command-buffer registers, triggers PSP, waits by interrupt or panic-safe polling, records PSP status, persists INIT_EX NV state for mutating commands, reclaims buffers, and copies results back. Ioctls validate access mode, copy user data, perform state transitions such as temporary INIT/SHUTDOWN, and return firmware status through `struct sev_issue_cmd`.

## State And Persistence Behavior

Global state includes `sev_cmd_mutex`, `misc_dev`, `psp_dead`, `psp_timeout`, `sev_es_tmr`, `sev_init_ex_buffer`, and the HV-fixed page list. Per-device `struct sev_device` stores firmware API/build, command buffers, platform status, SNP initialized state, SNP feature/status caches, waitqueue state, and TIO registration. INIT_EX data can persist to a root-opened file path. SNP page ownership state persists in the RMP and can force leaking pages if reclaim fails. HV-fixed pages may become non-returnable until reboot after SNP INIT_EX.

## Dependencies And Integration Points

This file integrates with PSP master/device state, SEV UAPI ioctls, KVM exported SEV guest APIs, x86 SNP/RMP helpers, AMD IOMMU SNP support, firmware loading, panic notifiers, PCI TSM/TIO helpers, cache flush/WBINVD operations, misc devices, and root filesystem file I/O for INIT_EX. `sev-dev-tio.c` supplies TIO command sizing and TSM initialization.

## Risks And Test Signals

Risks are high: command-buffer active flags can remain set on early preparation errors, SNP RMP transitions can leak or strand pages, panic shutdown must avoid mutex and notifier deadlocks, ioctl user-copy size limits must match firmware expectations, INIT_EX persistence can fail after successful firmware mutations, and TIO/SNP initialization ordering can lose state if probe deferral is misconfigured. Test signals include `/dev/sev` platform ioctl suites, KVM SEV/SEV-ES/SNP guest launch/teardown, SNP kexec and panic paths, firmware update/version logs, RMP page-state stress, INIT_EX file persistence, negative PSP status injection, and lockdep around nested reclaim commands.
