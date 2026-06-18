# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_npu.c

## Purpose
`airoha_npu.c` is the platform driver for Airoha Network Processor Unit firmware. It loads RV32/data firmware into reserved memory/MMIO SRAM, boots NPU cores, services mailbox and watchdog interrupts, and exposes NPU-backed PPE and WLAN offload operations to Ethernet and wireless consumers.

## Important APIs and functions
- `airoha_npu_probe()` maps the NPU register space, creates a regmap, resolves reserved memory and IRQs, initializes operation callbacks, loads/starts firmware, boots cores, queries firmware version, and stores driver data.
- `airoha_npu_run_firmware()` loads either `firmware-name` entries from devicetree or SoC-default firmware names into reserved memory and local SRAM.
- `airoha_npu_send_msg()` is the central mailbox path. It DMA-maps a request object, writes mailbox buffer address/size/doorbell fields, waits for `MBOX_MSG_DONE`, checks status, and unmaps the buffer.
- PPE operations include `airoha_npu_ppe_init()`, `airoha_npu_ppe_deinit()`, `airoha_npu_ppe_flush_sram_entries()`, `airoha_npu_foe_commit_entry()`, and `airoha_npu_ppe_stats_setup()`.
- WLAN operations include `airoha_npu_wlan_msg_send()`, `airoha_npu_wlan_msg_get()`, `airoha_npu_wlan_init_memory()`, queue-address helpers, and IRQ status/mask helpers.
- `airoha_npu_get()` and `airoha_npu_put()` are exported supplier lookup/module-reference helpers used by consumers through an `airoha,npu` phandle.
- IRQ paths: `airoha_npu_mbox_handler()` acknowledges firmware mailbox interrupts; `airoha_npu_wdt_handler()` schedules `airoha_npu_wdt_work()`, which emits a small devcoredump with PC/SP/LR.

## Control flow
Probe first maps hardware and installs callback function pointers into `npu->ops`. It then requests one mailbox IRQ, per-core watchdog IRQs, and stores WLAN IRQ numbers. Firmware loading validates sizes, writes images, programs NPU MIB/boot registers, sets all boot bases to reserved memory start, and triggers cores. Consumers later call `airoha_npu_get()`, which resolves the phandle platform device, pins the module, and creates a device link. PPE or WLAN requests are packaged as mailbox payloads and synchronously sent to core 0.

## State and persistence behavior
The driver owns volatile firmware images in device memory, a regmap, per-core locks/work items, cached WLAN IRQ numbers, and an optional `npu->stats` IO mapping returned by firmware for PPE stats. It persists no host-side data across reload. Reserved-memory names such as `tx-bufid`, `pkt`, `tx-pkt`, and optional `ba` are used to pass physical addresses to firmware.

## Dependencies and integration points
This file depends on platform/OF infrastructure, firmware loading, reserved-memory APIs, regmap MMIO, DMA mapping, devcoredump, and `airoha_offload` NPU/PPE/WLAN contracts. It is a supplier for Airoha Ethernet PPE setup and likely WLAN drivers. Firmware files are declared through `MODULE_FIRMWARE`.

## Risks and edge cases
`airoha_npu_send_msg()` uses a fixed core index marked `FIXME`, so multicore mailbox routing is not generalized. It waits up to 100 seconds in an atomic poll while holding a spinlock, which makes firmware stalls high impact. Firmware names and reserved-memory regions are mandatory unless devicetree overrides are complete. `airoha_npu_get()` must balance module/device references through `airoha_npu_put()`. Watchdog coredumps are intentionally small and may not capture enough state for deep firmware failures.

## Test signals
Probe should log firmware version when `WLAN_FUNC_GET_WAIT_NPU_VERSION` succeeds. Tests should cover missing firmware returning probe defer, reserved-memory lookup failures, mailbox timeout/error status, PPE init/deinit, PPE stats setup, WLAN reserved-memory setup, watchdog interrupt coredump generation, module reference balancing, and consumer device-link behavior.
