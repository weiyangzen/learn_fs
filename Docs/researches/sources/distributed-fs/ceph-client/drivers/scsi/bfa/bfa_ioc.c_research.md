# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc.c

## Purpose

`bfa_ioc.c` is the common IOC and service-module implementation for the BFA Fibre Channel driver. It owns IOC enable/disable/failure state machines, IOCPF firmware boot and synchronization, firmware image compatibility decisions, mailbox send/receive and class dispatch, heartbeat monitoring and recovery, adapter identity reporting, timer infrastructure, firmware trace/core/statistics access, and mailbox-backed service modules for ASIC block configuration, SFP, flash, diagnostics, PHY, driver configuration, FRU/VPD, TFRU, and raw flash reads.

## Important APIs, Types, and Functions

Core APIs include lifecycle/PCI setup (`bfa_ioc_attach()`, `bfa_ioc_detach()`, `bfa_ioc_pci_init()`, `bfa_ioc_mem_claim()`, `bfa_ioc_enable()`, `bfa_ioc_disable()`, `bfa_ioc_suspend()`), firmware/version functions (`bfa_ioc_boot()`, `bfa_ioc_fwver_get()`, `bfa_ioc_fwver_cmp()`, `bfa_ioc_fwsig_invalidate()`), mailbox APIs, state/attribute APIs, debug/statistics APIs, and timer APIs.

Service modules implemented here include ABLK configuration, SFP show/media/speed, flash attributes/erase/update/read, diagnostics memtest/fwping/temperature/LED/beacon, PHY query/stats/read/update, dconf flash-backed driver configuration, FRU/TFRU read/write, and low-level raw flash access.

## Control Flow

Attach initializes mailbox state, notification list, and the IOC FSM. PCI setup records device/class identity, derives ASIC generation and personality, selects ASIC-specific IOC hardware hooks, maps the port, and initializes registers. Enable delegates from the outer IOC FSM to IOCPF, which checks firmware state, firmware image compatibility, hardware semaphores, firmware locks, and peer IOC sync before booting or reusing firmware. Boot initializes PLL/LMEM, downloads firmware from driver image or flash, writes boot metadata into SMEM, starts LPU, polls for firmware readiness, sends IOC enable, and then GETATTR.

Operational entry calls the driver enable callback, notifies registered modules, starts heartbeat monitoring, logs enable, and posts AEN. Heartbeat compares firmware heartbeat count and polls queued mailboxes; lack of progress triggers recovery. Failure paths save firmware trace, notify callbacks/modules, flush mailboxes, stop LPU where needed, update firmware state, coordinate sync, and either auto-recover or remain failed. Disable sends IOC disable, waits or times out, leaves sync, flushes pending mailbox commands, and notifies modules.

Mailbox flow is shared across modules. Commands send immediately if the host command register is free; otherwise they queue. ISR and heartbeat polling drain the queue. I2H messages of class IOC are handled internally; other classes dispatch to registered module handlers.

Service modules follow a common asynchronous pattern: attach registers mailbox and IOC notification handlers; memclaim stores DMA buffers; public APIs check IOC state and busy flags, populate request state and callbacks, queue a mailbox command, and complete in ISR by endian-converting status, copying DMA buffers, continuing chunked transfers, clearing busy state, and invoking callbacks. Dconf adds a deferred flash persistence state machine with dirty debounce and final sync. Raw flash reads bypass firmware and program FLI registers under a flash semaphore.

## State and Persistence Behavior

Persistent device state includes firmware in SMEM, flash partitions, driver config, FRU/VPD/TFRU, and firmware state registers. Runtime state includes IOC/IOCPF FSMs, timers, heartbeat count, mailbox queue, notify queue, hardware interface, adapter attributes, firmware trace save buffer, service-module busy flags, DMA buffers, dconf dirty/sync state, and global `bfa_auto_recover`. Flash, dconf, FRU, and TFRU write paths modify adapter nonvolatile storage.

## Dependencies and Integration Points

The file depends on BFA/BFI headers, Linux MMIO/delay/time/endian/list helpers, ASIC-specific IOC hardware files, firmware image callbacks, BFAD enable/disable/reset/heartbeat callbacks, BFI mailbox classes, IOCFC dconf events, AEN posting, and higher-level management callers.

## Risks and Edge Cases

The IOC/IOCPF state machines are semaphore-, timer-, and peer-sync-sensitive; missed releases or events can wedge enable/disable. `bfa_ioc_adapter_is_disabled()` appears to check current firmware state twice rather than alternate state for multi-function adapters. Enable/disable timestamps use a suspicious endian helper direction. `bfa_timer_stop()` assumes active timers. Generic mailbox flush drops queued commands without direct callbacks, relying on module notifications. Service-module busy flags can remain set if callbacks or IOC notifications are missed. Raw flash access uses busy-wait loops and must release the semaphore on every error. PHY write endian conversion direction looks questionable. Flash APIs enforce alignment that callers must respect.

## Test Signals

Validate enable/disable, firmware mismatch, firmware boot source selection, IOCPF timeout/semaphore failures, heartbeat recovery, mailbox queue drain, GETATTR and adapter identity, trace/core/stat reads, ABLK config, SFP events and speed validation, flash chunked read/write/erase and alignment errors, diagnostics, PHY operations, dconf dirty/final sync and IOC-down resume, FRU/TFRU gating and chunking, and raw flash FIFO-boundary/semaphore behavior.
