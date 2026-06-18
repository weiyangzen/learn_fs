# sources/distributed-fs/ceph-client/drivers/thunderbolt/domain.c

## Purpose

`domain.c` implements the Thunderbolt bus and domain core. It registers the `thunderbolt` bus type, matches Thunderbolt services to service drivers, exposes domain sysfs attributes, allocates and tears down `struct tb` domains, coordinates control-channel lifecycle with connection-manager operations, handles suspend/resume/runtime PM transitions, and provides authorization/path-management wrappers.

## Important APIs, Types, and Functions

Service bus helpers include `match_service_id()`, `tb_service_match()`, `tb_service_probe()`, `tb_service_remove()`, and `tb_service_shutdown()`. Domain sysfs attributes are `boot_acl`, `deauthorization`, `iommu_dma_protection`, and `security`.

Public domain lifecycle APIs include `tb_domain_alloc()`, `tb_domain_add()`, `tb_domain_remove()`, `tb_domain_suspend_noirq()`, `tb_domain_resume_noirq()`, `tb_domain_suspend()`, `tb_domain_freeze_noirq()`, `tb_domain_thaw_noirq()`, `tb_domain_complete()`, `tb_domain_runtime_suspend()`, `tb_domain_runtime_resume()`, `tb_domain_init()`, and `tb_domain_exit()`.

Authorization and path APIs include `tb_domain_disapprove_switch()`, `tb_domain_approve_switch()`, `tb_domain_approve_switch_key()`, `tb_domain_challenge_switch_key()`, `tb_domain_disconnect_pcie_paths()`, `tb_domain_approve_xdomain_paths()`, `tb_domain_disconnect_xdomain_paths()`, and `tb_domain_disconnect_all_paths()`.

## Control Flow

`tb_domain_alloc()` allocates `struct tb` plus connection-manager private data, assigns a domain id, creates an ordered workqueue, allocates the control channel with `tb_domain_event_cb()`, initializes the embedded device, and sets bus/type/groups. `tb_domain_add()` starts the control channel under `tb->lock`, calls connection-manager `driver_ready`, adds the domain device, starts the connection manager, releases the lock to allow event processing, and enables runtime PM/autosuspend.

Control-channel events enter `tb_domain_event_cb()`. XDomain request/response packets are delegated to XDomain handling when enabled; other events are passed to `cm_ops->handle_event()`.

Removal locks the domain, stops connection-manager activity, stops control traffic, flushes the ordered workqueue, calls optional `deinit`, and unregisters the device. The device release frees the control channel, workqueue, ida id, mutex, and `struct tb`.

Suspend/freezing stop the control channel after optional connection-manager noirq hooks. Resume/thaw restart it before optional resume hooks. Runtime suspend calls optional connection-manager runtime suspend and then stops control traffic; runtime resume starts control traffic then calls the resume hook.

Authorization wrappers enforce connection-manager capability and parent authorization before approving a switch. Secure challenge approval generates a random challenge, asks firmware/device for a response, computes HMAC-SHA256 using the switch key, uses `crypto_memneq()` for comparison, and approves only on match.

## State and Persistence Behavior

Domain state persists in `struct tb`: NHI, control channel, ordered workqueue, device model object, security level, boot ACL capacity, domain lock, root switch, and connection-manager private data. The bus registration and domain ida are global.

Sysfs `boot_acl` can persist policy into firmware-managed preboot ACL storage through connection-manager callbacks. Switch authorization, key approval, challenge approval, and path disconnect/approval can change controller and topology state but are not stored by this file itself.

## Dependencies and Integration Points

The file depends on the Linux driver core, bus types, sysfs attributes, runtime PM, IDA, workqueues, crypto SHA256/HMAC helpers, random bytes, the Thunderbolt control channel, XDomain support, NVM/ACPI/debugfs initialization, and connection-manager operations in `struct tb_cm_ops`.

It is the integration point between low-level NHI probing, firmware/software connection managers, switch/device objects, XDomain services, debugfs, ACPI, NVM, and sysfs userspace policy.

## Risks and Edge Cases

`boot_acl_store()` carefully bounds input length and requires exactly `nboot_acl` comma-separated fields, but it calls `pm_runtime_get_sync()` without checking negative return. Similar patterns elsewhere assume runtime PM resume success or tolerate later command failures.

Domain start holds `tb->lock` across control-channel start because events may arrive immediately. Any connection-manager `driver_ready` or `start` implementation must avoid lock inversions with work queued back to the same ordered workqueue.

Runtime resume starts the control channel before the connection manager resumes. If resume hook fails, the control channel remains started; callers need to handle the partially resumed state.

Authorization wrappers require parent authorization but trust `sw->key` and firmware callbacks for secure operations. Challenge approval returns `-EKEYREJECTED` on HMAC mismatch and must be tested with malformed or missing keys.

## Test Signals

Tests should cover bus registration/unregistration, service matching by all match flags, probe/remove/shutdown dispatch, domain allocation failure unwind, add failure at driver_ready/device_add/start stages, event callback routing, sysfs boot ACL show/store parsing, suspend/resume/freeze/thaw/runtime PM sequencing, switch approval parent checks, secure challenge success/failure, and disconnect-all behavior across PCIe and XDomain paths.
