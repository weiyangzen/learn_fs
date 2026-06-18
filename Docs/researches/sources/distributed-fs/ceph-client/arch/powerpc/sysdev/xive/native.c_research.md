# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/native.c

## Purpose
`native.c` implements the XIVE backend for PowerNV systems running against OPAL/skiboot. It supplies the generic core with OPAL-backed interrupt source discovery, source programming, queue setup, TIMA acknowledgement, IPI allocation, CPU setup, shutdown, and debug hooks. It also exports native XIVE helper APIs used by KVM and other PowerNV code for VP and queue management.

## Important APIs, Types, And Functions
Backend callbacks are collected in `xive_native_ops`. Important backend functions include `xive_native_populate_irq_data`, `xive_native_configure_irq`, `xive_native_configure_queue`, `xive_native_disable_queue`, `xive_native_setup_queue`, `xive_native_cleanup_queue`, `xive_native_update_pending`, CPU prepare/setup/teardown callbacks, IPI get/put callbacks, and `xive_native_shutdown`. Exported helper APIs include IRQ allocation/free, VP block allocation/free, VP enable/disable/info, queue info/state get/set, feature probes for single escalation/save-restore, and sync helpers.

## Control Flow
`xive_native_init` locates the OPAL XIVE device tree node, maps the hypervisor TIMA window, chooses the queue size and maximum priority, records KVM TIMA mappings, reads provisioning configuration, switches OPAL to exploitation mode, allocates pool VPs, and calls `xive_core_init`. Interrupt data population asks OPAL for source flags/pages, maps EOI and trigger pages, and records LSI/StoreEOI attributes. Queue configuration asks OPAL for queue info, initializes queue indexes and masks, sets `OPAL_XIVE_EQ_ALWAYS_NOTIFY | OPAL_XIVE_EQ_ENABLED`, optionally enables escalation, and publishes `q->qpage` after a write barrier. Interrupt acknowledgement reads `TM_SPC_ACK_HV_REG`, derives CPPR and HE, and marks pending priorities for the generic scanner.

## State And Persistence
Runtime state includes queue shift, provisioning page size/chip list/cache, pool VP base, and capability booleans. OPAL mode is changed from emulation to exploitation during init and reset to emulation during shutdown. Queue pages and provisioning pages are kernel allocations; donated provisioning pages are intentionally ignored by kmemleak. VP, queue, and IRQ state live in firmware and are accessed through OPAL calls.

## Dependencies And Integration Points
This file depends on OPAL XIVE calls, PowerNV machine init, device tree properties such as `ibm,opal-xive-pe`, `ibm,xive-eq-sizes`, provisioning properties, TIMA registers, `kvmppc_set_xive_tima`, and generic XIVE core contracts. KVM integration is substantial through exported VP, queue, escalation, save/restore, and TIMA APIs.

## Risks
OPAL calls can return `OPAL_BUSY` or `OPAL_XIVE_PROVISIONING`; retry and provisioning paths must remain correct or initialization and KVM VP allocation fail. MMIO mappings must be cleaned correctly when trigger and EOI pages alias. Publishing `q->qpage` before queue fields are visible would race KVM IPI EOI logic. Firmware capability mismatches around queue state, VP save/restore, and single escalation affect migration and virtualization.

## Test Signals
Signals include successful PowerNV boot with native XIVE, OPAL exploitation-mode entry, MSI/LSI delivery, IPI allocation/free, KVM XIVE guests, VP block allocation under provisioning pressure, queue state save/restore tests when firmware supports it, and debugfs exposure of `save-restore`.
