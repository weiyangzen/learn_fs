# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_minidump.c

### Purpose
`qlcnic_minidump.c` implements QLogic qlcnic firmware minidump capture. It loads a firmware-provided dump template, interprets template entries, reads selected adapter registers/memory/flash/cache regions, and stores the captured dump in `adapter->ahw->fw_dump` for later collection.

### Important APIs, Types, And Functions
The file defines packed template entry payloads such as `__crb`, `__ctrl`, `__cache`, `__mem`, `__mux`, `__queue`, `__pollrd`, `__mux2`, and `__pollrdmwr`, plus opcode-to-handler tables for 82xx and 83xx hardware. Public entry points include `qlcnic_fw_cmd_get_minidump_temp()`, `qlcnic_dump_fw()`, and `qlcnic_83xx_get_minidump_template()`. Template header helpers cache version, capability masks, saved-state accessors, and system-info fields for both 82xx and 83xx layouts.

### Control Flow
Template acquisition first asks firmware for size/version, falls back to flash for 83xx, DMA-reads the template when possible, verifies checksum, caches header fields, optionally allocates a PEX DMA buffer, and enables dump state. Capture checks that a template exists, dump capture is enabled, and the previous dump was cleared. It computes required dump size from enabled capability masks, allocates `fw_dump->data`, writes driver/firmware version into the template header, then walks template entries. Each enabled entry dispatches to its opcode handler and is skipped if the handler size does not match the template's `cap_size`. Completion marks `fw_dump->clr` and emits a `FW_DUMP=<netdev>` uevent.

### State, Persistence, And Dependencies
Persistent driver state is in `struct qlcnic_fw_dump`: template header, template size/version, capability mask, data buffer, clear flag, and optional DMA buffer/physical address. Hardware state is accessed through qlcnic indirect register helpers, shared flash locks, 83xx flash readers, mailbox commands, memory test-agent registers, and PEX DMA engines. The dump itself is in kernel memory until cleared by higher-level driver paths.

### Integration Points
The file plugs into qlcnic hardware ops through template-header helper callbacks and into diagnostic/ethtool dump flows through `qlcnic_dump_fw()`. 83xx firmware-update paths can refresh templates when firmware version increases and can request extended iSCSI dump capability on QLE8830 devices.

### Risks
The code executes template-directed register writes and polling, so malformed templates can hang capture, skip data, or touch unintended device windows. Memory reads require alignment and size multiples for the test-agent path. PEX DMA has fallback behavior, but DMA descriptor setup and saved-state DMA-engine index must be valid. `qlcnic_read_memory_test_agent()` appears to increment the local `ret` pointer rather than a byte counter in the loop, which is suspicious even though the function returns `mem->size`. Flash access and dump buffers must be serialized by existing locks and clear-state checks.

### Test Signals
Useful signals include successful template load from firmware and flash, checksum-failure rejection, capture with each supported opcode, disabled capture rejection, previous-dump-not-cleared rejection, PEX DMA unavailable fallback to test-agent reads, uevent generation, and validation that captured section sizes match template `cap_size`.
