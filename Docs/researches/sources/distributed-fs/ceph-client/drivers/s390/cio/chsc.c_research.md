# sources/distributed-fs/ceph-client/drivers/s390/cio/chsc.c

## Purpose
This file implements the common in-kernel Channel Subsystem Call (CHSC) services. It issues CHSC requests for subchannel, QDIO, channel-path, measurement, SCM, PNSO, GIB, and control-unit information; processes Store Event Information notifications from CSS CRWs; and propagates channel-path/resource events to CSS and CCW devices.

## Important APIs, Types, and Functions
Exports include `chsc_notifier_register()`, `chsc_error_from_response()`, `chsc_get_ssd_info()`, `chsc_ssqd()`, `chsc_sadc()`, `chsc_chp_online()`, `chsc_chp_offline()`, `chsc_chp_vary()`, `__chsc_do_secm()`, `chsc_secm()`, channel-path descriptor helpers, `chsc_get_channel_measurement_chars()`, `chsc_init()`, `chsc_enable_facility()`, `chsc_determine_css_characteristics()`, `chsc_siosl()`, `chsc_scm_info()`, `chsc_pnso()`, `chsc_sgib()`, and `chsc_scud()`. Shared globals are serialized CHSC/SEI pages, `chsc_page_lock`, `chsc_notifiers`, and exported `css_general_characteristics`/`css_chsc_characteristics`.

## Control Flow
Synchronous helpers allocate or reuse a page-aligned request area, fill CHSC headers/opcodes, issue `chsc()`, translate condition/response codes, and copy result payloads to caller structures. `chsc_process_crw()` handles CSS CRWs by repeatedly issuing SEI requests, with an old-firmware fallback when notification type masks are unsupported. NT0 events fan out to link-incident logging, resource accessibility scans, channel-path availability/configuration processing, SCM updates, AP config notifiers, and FCES path events. Channel-path online/offline/vary helpers update descriptors, wait for existing slow-path work, iterate affected subchannels, and schedule reprobes.

## State and Persistence
All state is in kernel memory or hardware-managed CHSC/CSS structures. `sei_page` and `chsc_page` are allocated at init and freed on cleanup. CSS characteristics persist in exported globals after detection. Channel measurement enable state is stored in `channel_subsystem.cm_enabled` and CHSC-programmed CUB/ECUB addresses. No disk persistence exists.

## Dependencies and Integration Points
The file depends on low-level `chsc()`, CRW registration, CIO debug logs, SCLP/CHSC architecture structures, CSS iteration, channel-path registration, SCM bus hooks, zPCI event handlers, AP config notifier users, QDIO, and CMF/CSS measurement data. It is the main firmware boundary for `chp.c`, `css.c`, `device.c`, QDIO, SCM, PCI, and network subchannel code.

## Risks and Test Signals
Risk areas include one shared CHSC page requiring strict locking, firmware response-code mapping, unsupported-notification fallback behavior, event-overflow recovery, channel-path event races with slow-path scans, and copying variable-length CHSC response blocks. Test signals include CHSC response-code fault injection, CRW/SEI event injection for each content code, channel-path add/remove/vary tests, SECM enable/disable with sysfs attributes, QDIO SSQD/SADC callers, `css_general_characteristics` detection, SCM/zPCI/AP notification paths, and `chsc_scud()` validation of malformed response lengths.
