<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/smipcie-ir.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/smipcie-ir.c

Purpose: raw infrared receiver support for SMI PCIe cards. It configures IR sampling registers, decodes hardware duration bytes into `ir_raw_event`s, and registers an RC-core raw IR device.

Important APIs, types, and functions: `smi_ir_init()` allocates and registers `rc_dev`. `smi_ir_start()` programs idle/sample timing and enables hardware. `smi_ir_irq()` disables/clears/decodes/re-enables IR interrupts. `smi_ir_decode()` reads FIFO data and high-idle state. `smi_raw_process()` converts bytes into pulse/space durations. `smi_ir_exit()` unregisters and stops the RC device.

Control flow: probe calls init, then after IRQ request calls start. The shared PCI IRQ calls `smi_ir_irq()` when `IR_X_INT` is set. Decoding reads `IR_Data_Cnt`, fetches packed bytes from `IR_DATA_BUFFER_BASE`, stores raw events, adds idle spaces, and triggers `ir_raw_event_handle()`.

State and persistence: `struct smi_rc` stores device pointers, names, and a 256-byte decode buffer. RC map name comes from board config. No persistent storage.

Dependencies and integration points: RC core raw decoders, SMI register macros, main IRQ handler, board `rc_map`.

Risks: `smi_ir_exit()` calls `rc_unregister_device()`, then `smi_ir_stop()`, then `rc_free_device()`; RC core ownership conventions should be checked because unregister may already free in some patterns. `ir_count` is trusted against a 256-byte buffer. IR is mandatory in probe.

Test signals: RC device appears, keypresses decode with board map, IRQ storm absence, suspend/remove cleanup, and high-idle events produce frame gaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/smipcie-ir.c -->
