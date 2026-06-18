# subset-b-004122 Research

Grouped source-tree-aligned research for the Mantis, MGB4, and NetUP media PCI files in subset B.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_cards.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_cards.c

- Purpose: PCI entry point for the Mantis DVB bridge driver; binds supported TwinHan/TechniSat/TerraTec subsystem IDs to board-specific frontend configurations and coordinates all subsystem setup.
- Important APIs/types/functions: module parameter `verbose`, `mantis_irq_handler()`, `mantis_pci_probe()`, `mantis_pci_remove()`, `mantis_pci_table`, and `mantis_pci_driver`.
- Control flow: Probe allocates `struct mantis_pci`, installs the board IRQ callback, initializes PCI/MMIO, routes TS to HIF, registers I2C, reads EEPROM MAC, allocates DMA, registers DVB, input, and UART. Remove unwinds in reverse. The ISR acknowledges MMIO interrupt status, schedules DMA bottom-half work for RISC interrupts, wakes I2C/HIF waits, and schedules UART/HIF work.
- State and persistence: Runtime state lives in `struct mantis_pci`: interrupt masks/status, work items, DVB objects, I2C adapter, DMA buffers, CA state, and rc-core device. No disk persistence; EEPROM MAC is read but not copied into `mac_address` here.
- Dependencies and integration points: Integrates Linux PCI, IRQ, workqueue, rc-core, DVB demux/frontend/net, board configs from `mantis_vp*`, and local PCI/I2C/DMA/DVB/UART/input/CA modules.
- Risks: Shared IRQ handling depends on correct mask/status acknowledgement; IRQ0 assumes `mantis_ca` exists when CAM support is active; teardown must cancel work before freeing MMIO-backed state; `devs` monotonically increments and is not decremented.
- Test signals: Build with all referenced frontend modules; probe/remove on supported PCI IDs; exercise DMA demux, I2C frontend attach, IR UART IRQ, and CAM insert/remove interrupts while checking for lost IRQs or use-after-free on unload.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_common.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_common.h

- Purpose: Shared Mantis definitions: debug macro, MMIO helpers, PCI ID helpers, board configuration contract, and the central device state object.
- Important APIs/types/functions: `dprintk`, `mmread/mmwrite`, `MAKE_ENTRY`, `enum mantis_i2c_mode`, `struct mantis_hwconfig`, `struct mantis_pci_drvdata`, `struct mantis_pci`, `mantis_mask_ints()`, `mantis_unmask_ints()`.
- Control flow: Consumers include this header to access MMIO through the local `mantis` variable convention and to mutate device-wide state. Board files fill `mantis_hwconfig`; probe copies it into `mantis_pci`; helpers serialize interrupt mask updates with `intmask_lock`.
- State and persistence: `struct mantis_pci` owns all live kernel resources: PCI/MMIO, RISC DMA buffers, workqueues, I2C adapter, DVB adapter/demux, frontend pointer, CA state, UART work, and rc-core state. It is volatile per-device state only.
- Dependencies and integration points: Connects Linux PCI, DVB, I2C, workqueue, mutex/spinlock, UART and CAM link headers. `MAKE_ENTRY` embeds compound-literal driver data in PCI ID rows.
- Risks: The debug macro assumes a visible variable named `mantis`; misuse in another scope will fail or log the wrong device. Interrupt helpers require valid MMIO and initialized spinlock. Compound literal lifetime in static PCI tables relies on file-scope static storage semantics.
- Test signals: Compile coverage is the main header test; runtime signals are correct verbose logging, safe interrupt mask transitions, and board configs carrying sane power/reset/I2C/TS settings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dma.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dma.c

- Purpose: Implements the Mantis transport-stream DMA path using a coherent circular buffer and a small RISC program executed by the bridge.
- Important APIs/types/functions: `mantis_dma_init()`, `mantis_dma_exit()`, `mantis_dma_start()`, `mantis_dma_stop()`, `mantis_dma_xfer()`, internal buffer allocator, and RISC instruction macros.
- Control flow: Initialization allocates a 64 KiB coherent TS buffer and one page of coherent RISC code. Start builds WRITE commands for four 16 KiB blocks with 2 KiB transfers, points hardware at the RISC program, unmasks RISC interrupts, and enables FIFO/DCAP/RISC. IRQ updates `busy_block`; bottom-half work filters completed blocks into the DVB demux until `last_block` catches up. Stop disables hardware and masks DMA interrupts.
- State and persistence: State is held in `buf_cpu/buf_dma`, `risc_cpu/risc_dma`, `last_block`, and `busy_block`; no persistence. The ring position is reconstructed at stream start.
- Dependencies and integration points: Feeds `dvb_dmx_swfilter()` or `dvb_dmx_swfilter_204()` according to board TS size; uses DMA coherent allocation and Mantis MMIO registers from `mantis_reg.h`.
- Risks: The ring is small and can overrun if bottom-half work is delayed. RISC program size depends on constants fitting in one page. Work and IRQ state must be stopped before freeing coherent buffers. `busy_block` is shared with ISR without an explicit lock.
- Test signals: Validate with sustained DVB capture for 188-byte and 204-byte TS boards, stream start/stop loops, module unload under streaming, and debug logs showing monotonic block advancement without queue stalls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dma.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dma.h

- Purpose: Public declaration header for the Mantis DMA lifecycle and bottom-half transfer routine.
- Important APIs/types/functions: `mantis_dma_init`, `mantis_dma_exit`, `mantis_dma_start`, `mantis_dma_stop`, and `mantis_dma_xfer`.
- Control flow: Included by probe/DVB code: probe allocates buffers, DVB feed callbacks start/stop hardware, and workqueue setup uses `mantis_dma_xfer`.
- State and persistence: No state; it exposes functions operating on `struct mantis_pci` fields defined in `mantis_common.h`.
- Dependencies and integration points: Depends on `struct mantis_pci` and `struct work_struct` being visible through including compilation units.
- Risks: Prototype drift would break DMA/DVB integration. It intentionally exposes start/stop separately from allocation, so callers must preserve lifecycle order.
- Test signals: Compile and link coverage plus stream start/stop tests in `mantis_dvb.c`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dvb.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dvb.c

- Purpose: Registers the DVB adapter, demux, dmxdev, DVB net device, hardware/memory frontends, and board frontend for the Mantis bridge.
- Important APIs/types/functions: `mantis_frontend_power()`, `mantis_frontend_soft_reset()`, `mantis_dvb_init()`, `mantis_dvb_exit()`, feed callbacks, and module adapter-number option.
- Control flow: Init registers a DVB adapter, initializes demux and dmxdev, adds frontends, connects hardware input, initializes DVB net, configures DMA work, calls board `frontend_init`, then registers the frontend. Feed start increments `feeds` and starts DMA on the first feed; feed stop decrements and stops DMA at zero.
- State and persistence: Tracks active feed count, frontend pointer, demux objects, and work item in `struct mantis_pci`. No persistence; frontend power/reset lines are hardware state controlled over GPIO.
- Dependencies and integration points: Depends on DVB core/demux/net, local DMA and GPIO helpers, and each board frontend attachment implementation.
- Risks: Feed count is not protected by a lock. Error unwind must keep DVB object release order exact. Frontend power/reset has fixed sleeps and board-specific GPIO assumptions. `mantis->fe` is passed into board init before assignment by many boards.
- Test signals: Test with adapter registration, frontend attach failure paths, scan/tune, multiple demux consumers, feed start/stop races, and unload after failed or active frontend registration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dvb.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dvb.h

- Purpose: Declares Mantis DVB power/reset and adapter lifecycle APIs.
- Important APIs/types/functions: `enum mantis_power`, `mantis_frontend_power`, `mantis_frontend_soft_reset`, `mantis_dvb_init`, and `mantis_dvb_exit`.
- Control flow: Board files use power/reset helpers before `dvb_attach`; probe/remove use init/exit around DMA and input/UART setup.
- State and persistence: No state; functions mutate `struct mantis_pci` GPIO and DVB fields.
- Dependencies and integration points: Integrates with board-specific frontend modules and `mantis_ioc` GPIO helpers.
- Risks: Incorrect enum usage or lifecycle order can leave frontend power enabled or DVB objects partially registered.
- Test signals: Compile coverage and board attach tests for all Mantis DVB-S/S2/C/T variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dvb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_evm.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_evm.c

- Purpose: Host-interface event manager for CAM/PCMCIA smart-buffer events and CAM insertion/removal notifications.
- Important APIs/types/functions: `mantis_hifevm_work()`, `mantis_evmgr_init()`, and `mantis_evmgr_exit()`.
- Control flow: IRQ0 schedules `hif_evm_work`. The worker reads GPIF status, handles plugin/unplug by resetting card state and notifying DVB CA EN50221, logs HIF status bits, and wakes HIF operation waiters when smart-buffer operation completes. Init sets work, initializes PCMCIA, schedules an initial scan, then initializes HIF; exit flushes work and tears down HIF/PCMCIA.
- State and persistence: Uses `mantis_ca` slot state, `hif_event`, wait queues, and `sbuf_status`; no persistence.
- Dependencies and integration points: Depends on GPIF registers, `mantis_pcmcia`, `mantis_hif`, and DVB CA EN50221 callbacks.
- Risks: Worker uses MMIO and CA state asynchronously, so teardown ordering is important. CAM event debounce is minimal and hardware-specific. Wait logic depends on IRQ status being copied into `mantis->gpif_status` by the top-half.
- Test signals: Test CAM insertion/removal, EN50221 userspace notifications, HIF read/write completion waits, and unload while events are pending.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_evm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_hif.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_hif.c

- Purpose: Implements the Mantis host interface for CAM memory and I/O space accesses through GPIF smart-buffer registers.
- Important APIs/types/functions: `mantis_hif_read_mem`, `mantis_hif_write_mem`, `mantis_hif_read_iom`, `mantis_hif_write_iom`, `mantis_hif_init`, `mantis_hif_exit`, and internal wait helpers.
- Control flow: Each access locks `ca_lock`, composes GPIF address bits for memory or I/O space, writes byte count/address/data registers, waits for smart-buffer opdone or write-ack, reads/writes data, and unlocks. Init configures slot slave timing and GPIF IRQ masks; exit clears BRRDY mask.
- State and persistence: Uses `slot[0].slave_cfg`, `hif_event`, `gpif_status`, and wait queues in `struct mantis_ca`; no persistent state.
- Dependencies and integration points: Integrated with `mantis_evm.c`, `mantis_pcmcia.c`, `mantis_link.h`, MMIO definitions, and EN50221 CAM access paths in the broader driver.
- Risks: Timeout checks compare `wait_event_timeout()` to `-ERESTARTSYS`, but that API returns 0 on timeout, so timeouts may be misreported. Fixed microsecond delays and single-slot assumptions make hardware timing fragile.
- Test signals: Exercise CAM attribute/common memory reads, I/O reads/writes, timeout injection, and concurrent EN50221 accesses while checking lock coverage and wakeups.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_hif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_hif.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_hif.h

- Purpose: Defines symbolic operation IDs for Mantis HIF memory and I/O transactions.
- Important APIs/types/functions: `MANTIS_HIF_MEMRD`, `MANTIS_HIF_MEMWR`, `MANTIS_HIF_IOMRD`, `MANTIS_HIF_IOMWR`.
- Control flow: These constants classify host-interface operations, while callable prototypes are exported through `mantis_link.h`.
- State and persistence: No state or persistence.
- Dependencies and integration points: Used by HIF/CAM code to describe GPIF operation types.
- Risks: Constants are not strongly typed; mismatches would only surface at call sites or logs.
- Test signals: Compile coverage and CAM HIF transaction tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_hif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_i2c.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_i2c.c

- Purpose: Linux I2C adapter implementation for the Mantis bridge, supporting page-mode byte transfers and a combined byte-mode register read path.
- Important APIs/types/functions: `mantis_i2c_xfer()`, `mantis_i2c_read()`, `mantis_i2c_write()`, `mantis_i2c_func()`, `mantis_i2c_init()`, and `mantis_i2c_exit()`.
- Control flow: Transfers are serialized by `i2c_lock`. Byte-mode recognizes a one-byte write followed by one-byte read and performs a compact hardware transaction. Other reads/writes loop per byte, program `MANTIS_I2CDATA_CTL`, and poll interrupt status bits for done/ack. Init registers an adapter and masks I2C done IRQ; exit unregisters it.
- State and persistence: Stores adapter, return code, wait queue, and mutex in `struct mantis_pci`; no persistent state. Poll loops are bounded by `TRIALS`.
- Dependencies and integration points: Used by EEPROM reads, frontend/tuner attach and configuration, and board-specific tuner functions; depends on Mantis MMIO register definitions and Linux I2C core.
- Risks: Polling loops may spin hard and do not consistently fail if ack polling exhausts in helper paths. Functionality advertises SMBus emulation although hardware behavior is custom. I2C done IRQ is masked, so wait queue path is effectively unused here.
- Test signals: Test all frontend attach paths, EEPROM read, tuner parameter writes, NACK/timeouts, and mixed combined-message sequences.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_i2c.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_i2c.h

- Purpose: Public declarations and simple flags for the Mantis I2C adapter.
- Important APIs/types/functions: `I2C_STOP`, `I2C_READ`, `mantis_i2c_init`, and `mantis_i2c_exit`.
- Control flow: Probe calls init before EEPROM/frontend access; remove calls exit after DVB teardown.
- State and persistence: No direct state; lifecycle functions operate on the I2C fields in `struct mantis_pci`.
- Dependencies and integration points: Depends on Linux I2C core through implementation files.
- Risks: Unused flag definitions can diverge from hardware register names in `mantis_reg.h`; lifecycle ordering remains the main concern.
- Test signals: Compile and board frontend attach tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_input.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_input.c

- Purpose: Registers an rc-core infrared input device and forwards UART-decoded scancodes to it.
- Important APIs/types/functions: `mantis_input_init()`, `mantis_input_exit()`, and `mantis_input_process()`.
- Control flow: Init allocates an `rc_dev`, fills PCI input IDs, device names, rc map, parent device, and registers it. UART work calls `mantis_input_process()` to emit `rc_keydown()`. Exit unregisters/frees the rc device.
- State and persistence: Stores `rc`, `device_name`, `input_phys`, and rc map pointer in `struct mantis_pci`; no persistence.
- Dependencies and integration points: Integrates with Linux rc-core and `mantis_uart.c`; rc-map names come from PCI ID driver data.
- Risks: `mantis_input_exit()` calls both `rc_unregister_device()` and `rc_free_device()`; depending on rc-core ownership this can be fragile. Unknown protocol is used for all scancodes.
- Test signals: Test rc device creation, key events from UART, empty-map boards, and unload after registration failure or no rc map.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_input.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_input.h

- Purpose: Declares the Mantis rc-core input lifecycle and scancode forwarding functions.
- Important APIs/types/functions: `mantis_input_init`, `mantis_input_exit`, and `mantis_input_process`.
- Control flow: Probe/remove call init/exit; UART decode calls process.
- State and persistence: No state; functions use `struct mantis_pci` rc fields.
- Dependencies and integration points: Integrates `mantis_cards.c` and `mantis_uart.c` with rc-core.
- Risks: The closing comment names UART rather than input, a cosmetic guard-label mismatch.
- Test signals: Compile coverage plus IR event tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ioc.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ioc.c

- Purpose: Miscellaneous board I/O control helpers: EEPROM MAC read, GPIF GPIO bit updates, and stream routing between HIF and CAM.
- Important APIs/types/functions: `mantis_get_mac()`, `mantis_gpio_set_bits()`, `mantis_stream_control()`, and internal `read_eeprom_bytes()`.
- Control flow: MAC read performs an I2C register read from EEPROM address 0x50 at offset 0x08 and logs it. GPIO helper updates `MANTIS_GPIF_ADDR` bit state and clears DOUT. Stream control toggles `MANTIS_BYPASS` in `MANTIS_CONTROL` to route TS toward HIF or CAM.
- State and persistence: Tracks current GPIO bitfield in `mantis->gpio_status`; EEPROM contents are persistent hardware data but this file only reads/logs them.
- Dependencies and integration points: Used by probe, DVB frontend power/reset, board LNB voltage callbacks, and CAM stream routing; depends on Mantis I2C and GPIF registers.
- Risks: `mantis_get_mac()` does not copy the read MAC into `mantis->mac_address`. GPIO updates read current GPIF address register and may mix address/control bits with GPIO state. Stream-control bit math uses `0xff - MANTIS_BYPASS` instead of a conventional mask.
- Test signals: Test EEPROM read success/failure, frontend power GPIO transitions, stream routing before DMA/CAM operation, and regression for MAC propagation expectations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ioc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ioc.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ioc.h

- Purpose: Defines GPIF GPIO line numbers, stream-routing enum, and IOC helper prototypes.
- Important APIs/types/functions: `GPIF_A00` through `GPIF_A14`, `enum mantis_stream_control`, `mantis_get_mac`, `mantis_gpio_set_bits`, `mantis_stream_control`.
- Control flow: Board configs reference GPIO numbers for power/reset and board callbacks invoke GPIO helpers; probe uses stream control and MAC read.
- State and persistence: No state; constants map to hardware lines.
- Dependencies and integration points: Integrated by board-specific frontend files and `mantis_cards.c`.
- Risks: GPIO constants are untyped and hardware-specific; wrong board config can drive incorrect lines.
- Test signals: Compile and board power/reset smoke tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ioc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_link.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_link.h

- Purpose: Shared CAM/PCMCIA/HIF data model and prototypes for the Mantis conditional-access path.
- Important APIs/types/functions: `enum mantis_sbuf_status`, `struct mantis_slot`, `enum mantis_slot_state`, `struct mantis_ca`, CAM event, PCMCIA, EVM, and HIF function prototypes.
- Control flow: CA code allocates/fills `struct mantis_ca`; IRQ/work handlers update slot state and wait queues; HIF functions provide EN50221 memory/I/O access.
- State and persistence: State includes four slot descriptors, wait queues, smart-buffer status/event bits, slot state, CA private pointer, EN50221 object, and mutex. No persistence.
- Dependencies and integration points: Ties DVB CA EN50221 integration to `mantis_evm.c`, `mantis_pcmcia.c`, `mantis_hif.c`, and the larger Mantis PCI object.
- Risks: The implementation only treats slot 0 as active although arrays are sized for four. Wait-queue and status fields are shared with IRQ/work contexts.
- Test signals: CAM insertion/removal, EN50221 application access, HIF timeout, and module unload tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pci.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pci.c

- Purpose: Low-level PCI resource setup and teardown for the Mantis bridge.
- Important APIs/types/functions: `mantis_pci_init()` and `mantis_pci_exit()`.
- Control flow: Init enables the PCI device, sets 32-bit coherent DMA mask, enables bus mastering, claims BAR0, ioremaps it, records latency/revision, requests the shared IRQ using the board-configured handler, and stores driver data. Exit frees IRQ, unmaps and releases BAR0, and disables the device.
- State and persistence: Stores MMIO pointer, latency, revision, and PCI device pointer in `struct mantis_pci`; no persistence.
- Dependencies and integration points: Called first by probe and last during remove; underpins every MMIO helper and interrupt path.
- Risks: `mantis_addr` is logged but not assigned. Error handling jumps through resource release steps, so any future changes must preserve exact ownership. Only a coherent mask is set, not streaming mask.
- Test signals: Probe failure injection, request_irq failure, BAR mapping failure, and unload after active interrupts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pci.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pci.h

- Purpose: Declaration header for Mantis PCI resource lifecycle.
- Important APIs/types/functions: `mantis_pci_init` and `mantis_pci_exit`.
- Control flow: Probe/remove call these around all higher-level subsystems.
- State and persistence: No state; operates on `struct mantis_pci`.
- Dependencies and integration points: Integrates `mantis_cards.c` with low-level PCI implementation.
- Risks: Header must stay synchronized with exported implementation.
- Test signals: Compile/link plus probe/remove tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pcmcia.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pcmcia.c

- Purpose: Handles CAM PCMCIA physical-layer insertion/removal state and GPIF interrupt mask changes.
- Important APIs/types/functions: `mantis_event_cam_plugin()`, `mantis_event_cam_unplug()`, `mantis_pcmcia_init()`, and `mantis_pcmcia_exit()`.
- Control flow: Init unmasks IRQ0, reads detect status, configures plugin or plugout interrupt mask, sets slot state, and notifies DVB CA. Plugin/unplug handlers debounce by current slot state, pulse card reset values, swap GPIF IRQ masks, and update slot state. Exit clears status and masks IRQ0.
- State and persistence: Maintains `ca->slot_state` and hardware GPIF IRQ mask/status; no persistence.
- Dependencies and integration points: Called by event-manager init/exit and IRQ0 work; integrates with DVB CA EN50221 notifications.
- Risks: The status clear expression combines negated masks in a way that may not clear both bits as intended. Debounce uses fixed delays and assumes only slot 0. Concurrent CAM events depend on serialized work handling.
- Test signals: Test hotplug jitter, initial plugged/empty boot state, repeated insert/remove, and module unload during CAM events.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pcmcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_reg.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_reg.h

- Purpose: Register map and bit definitions for Mantis interrupts, DMA, I2C, control, GPIF, PCMCIA, and UART-adjacent blocks.
- Important APIs/types/functions: Defines `MANTIS_INT_*`, `MANTIS_DMA_CTL` bits, `MANTIS_I2CDATA_CTL` fields, `MANTIS_CONTROL`, GPIF timing/status/address/data registers, and smart-buffer/card event bits.
- Control flow: All Mantis implementation files use these offsets with `mmread/mmwrite` to acknowledge interrupts, program DMA/RISC, drive I2C, route streams, manage CAM HIF, and handle PCMCIA events.
- State and persistence: No state; constants describe volatile device MMIO hardware.
- Dependencies and integration points: Central dependency for Mantis PCI, DMA, I2C, DVB, IOC, UART, HIF, and PCMCIA code.
- Risks: Duplicate macro names for `MANTIS_GPIF_PCMCIAREG/IOM` appear in different address contexts but same values. Any wrong bit definition can corrupt hardware state across multiple subsystems.
- Test signals: Compile coverage is necessary but insufficient; hardware register access tests through stream, I2C, CAM, and IRQ paths are required.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_uart.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_uart.c

- Purpose: Configures the Mantis UART used for IR remote scancode reception and schedules bottom-half decoding from IRQ1.
- Important APIs/types/functions: `mantis_uart_init()`, `mantis_uart_exit()`, internal `mantis_uart_setup()`, `mantis_uart_work()`, and `mantis_uart_read()`.
- Control flow: Init disables UART RX interrupt, programs parity/baud and byte threshold, flushes RX, enables hardware and IRQ1, and schedules an initial drain. IRQ1 masks itself and schedules work; the worker drains FIFO until empty or timeout, emits scancodes via input code, then unmasks IRQ1. Exit masks interrupt, disables UART RX interrupt, and flushes work.
- State and persistence: Uses `uart_work`, board UART parameters, and rc device in `struct mantis_pci`; no persistence.
- Dependencies and integration points: Depends on Mantis MMIO registers, interrupt mask helpers, and `mantis_input_process()`.
- Risks: Scancode assembly masks data to 6 bits per byte and treats status bits as frame/parity errors. The 10 ms drain budget may leave data if FIFO remains busy. Correct input teardown must occur after UART work is flushed.
- Test signals: Test IR key reception, parity/framing error handling, FIFO-full logs, IRQ masking/unmasking, and unload during incoming UART data.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_uart.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_uart.h

- Purpose: UART register offsets, status bits, baud/parity enums, and lifecycle prototypes for Mantis IR reception.
- Important APIs/types/functions: `MANTIS_UART_CTL/RXD/BAUD/STAT`, RX status bits, `enum mantis_baud`, `enum mantis_parity`, `mantis_uart_init`, `mantis_uart_exit`.
- Control flow: Board configs choose baud/parity/byte count; UART implementation programs the hardware and forwards decoded keys.
- State and persistence: No state; constants configure volatile UART registers.
- Dependencies and integration points: Included by `mantis_common.h`, board configs, and `mantis_uart.c`.
- Risks: Enum ordering must match arrays and hardware setup switch. Parity enum names/order should be checked against register semantics.
- Test signals: Compile plus IR remote hardware tests across boards.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_uart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1033.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1033.c

- Purpose: Board-specific frontend glue for the Mantis VP-1033 DVB-S/DSS card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches STV0299 demod at 0x68 plus LG TDQ-CS001F tuner programming and symbol-rate callback.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; uses a 204-byte TS path, power GPIF_A12, reset GPIF_A13, 9600-N UART, and a large STV0299 init table.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-1033 hardware, scan/tune for DVB-S/DSS, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_1033_DVB_S.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1033.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1033.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1033.h

- Purpose: Board declaration header for Mantis VP-1033.
- Important APIs/types/functions: Defines PCI subsystem ID macro(s) `MANTIS_VP_1033_DVB_S` and declares the exported `struct mantis_hwconfig` used by the PCI ID table.
- Control flow: Included by `mantis_cards.c` so `MAKE_ENTRY` can bind a matching PCI subsystem ID to the board configuration; implementation files provide the actual frontend attach logic.
- State and persistence: No runtime state or persistence.
- Dependencies and integration points: Depends on `mantis_common.h` for `struct mantis_hwconfig` and on DVB frontend types where voltage callback is declared.
- Risks: Incorrect IDs or missing extern declarations would prevent board matching or link-time resolution.
- Test signals: Compile coverage and PCI ID probe tests for the board.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1033.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1034.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1034.c

- Purpose: Board-specific frontend glue for the Mantis VP-1034 DVB-S/DSS card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches MB86A16 frontend at 0x08 with board voltage callback.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; drives polarization using GPIO 13/14 and writes GPIF DOUT after SEC voltage changes.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-1034 hardware, scan/tune for DVB-S/DSS, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_1034_DVB_S.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1034.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1034.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1034.h

- Purpose: Board declaration header for Mantis VP-1034.
- Important APIs/types/functions: Defines PCI subsystem ID macro(s) `MANTIS_VP_1034_DVB_S and `vp1034_set_voltage`` and declares the exported `struct mantis_hwconfig` used by the PCI ID table.
- Control flow: Included by `mantis_cards.c` so `MAKE_ENTRY` can bind a matching PCI subsystem ID to the board configuration; implementation files provide the actual frontend attach logic.
- State and persistence: No runtime state or persistence.
- Dependencies and integration points: Depends on `mantis_common.h` for `struct mantis_hwconfig` and on DVB frontend types where voltage callback is declared.
- Risks: Incorrect IDs or missing extern declarations would prevent board matching or link-time resolution.
- Test signals: Compile coverage and PCI ID probe tests for the board.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1034.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1041.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1041.c

- Purpose: Board-specific frontend glue for the Mantis VP-1041 DVB-S/S2 card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches STB0899 demod, STB6100 tuner, and optional LNBP21 attach.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; uses extensive STB0899 register tables, 188-byte TS, and shared power/reset GPIOs.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-1041 hardware, scan/tune for DVB-S/S2, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_1041_DVB_S2 plus TechniSat/TerraTec aliases.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1041.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1041.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1041.h

- Purpose: Board declaration header for Mantis VP-1041.
- Important APIs/types/functions: Defines PCI subsystem ID macro(s) `MANTIS_VP_1041_DVB_S2, SKYSTAR/CINERGY aliases` and declares the exported `struct mantis_hwconfig` used by the PCI ID table.
- Control flow: Included by `mantis_cards.c` so `MAKE_ENTRY` can bind a matching PCI subsystem ID to the board configuration; implementation files provide the actual frontend attach logic.
- State and persistence: No runtime state or persistence.
- Dependencies and integration points: Depends on `mantis_common.h` for `struct mantis_hwconfig` and on DVB frontend types where voltage callback is declared.
- Risks: Incorrect IDs or missing extern declarations would prevent board matching or link-time resolution.
- Test signals: Compile coverage and PCI ID probe tests for the board.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1041.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2033.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2033.c

- Purpose: Board-specific frontend glue for the Mantis VP-2033 DVB-C card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches TDA10021 fallback to TDA10023 CU1216 frontend and CU1216 tuner programming.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; reads PWM from EEPROM, gates I2C before tuner access, and uses 204-byte TS.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-2033 hardware, scan/tune for DVB-C, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_2033_DVB_C.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2033.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2033.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2033.h

- Purpose: Board declaration header for Mantis VP-2033.
- Important APIs/types/functions: Defines PCI subsystem ID macro(s) `MANTIS_VP_2033_DVB_C` and declares the exported `struct mantis_hwconfig` used by the PCI ID table.
- Control flow: Included by `mantis_cards.c` so `MAKE_ENTRY` can bind a matching PCI subsystem ID to the board configuration; implementation files provide the actual frontend attach logic.
- State and persistence: No runtime state or persistence.
- Dependencies and integration points: Depends on `mantis_common.h` for `struct mantis_hwconfig` and on DVB frontend types where voltage callback is declared.
- Risks: Incorrect IDs or missing extern declarations would prevent board matching or link-time resolution.
- Test signals: Compile coverage and PCI ID probe tests for the board.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2033.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2040.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2040.c

- Purpose: Board-specific frontend glue for the Mantis VP-2040 DVB-C card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches TDA10021 fallback to TDA10023 CU1216 frontend and CU1216 tuner programming.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; similar to VP-2033 with separate PCI IDs for Cinergy/CableStar, 204-byte TS.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-2040 hardware, scan/tune for DVB-C, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_2040_DVB_C plus CINERGY_C/CABLESTAR_HD2.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2040.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2040.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2040.h

- Purpose: Board declaration header for Mantis VP-2040.
- Important APIs/types/functions: Defines PCI subsystem ID macro(s) `MANTIS_VP_2040_DVB_C, CINERGY_C, CABLESTAR_HD2` and declares the exported `struct mantis_hwconfig` used by the PCI ID table.
- Control flow: Included by `mantis_cards.c` so `MAKE_ENTRY` can bind a matching PCI subsystem ID to the board configuration; implementation files provide the actual frontend attach logic.
- State and persistence: No runtime state or persistence.
- Dependencies and integration points: Depends on `mantis_common.h` for `struct mantis_hwconfig` and on DVB frontend types where voltage callback is declared.
- Risks: Incorrect IDs or missing extern declarations would prevent board matching or link-time resolution.
- Test signals: Compile coverage and PCI ID probe tests for the board.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2040.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp3030.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp3030.c

- Purpose: Board-specific frontend glue for the Mantis VP-3030 DVB-T card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches ZL10353 demod plus TDA665x tuner.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; uses byte-mode I2C, custom reset/power order, 188-byte TS, and ENV57H12D5 tuner limits.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-3030 hardware, scan/tune for DVB-T, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_3030_DVB_T.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp3030.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp3030.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp3030.h

- Purpose: Board declaration header for Mantis VP-3030.
- Important APIs/types/functions: Defines PCI subsystem ID macro(s) `MANTIS_VP_3030_DVB_T` and declares the exported `struct mantis_hwconfig` used by the PCI ID table.
- Control flow: Included by `mantis_cards.c` so `MAKE_ENTRY` can bind a matching PCI subsystem ID to the board configuration; implementation files provide the actual frontend attach logic.
- State and persistence: No runtime state or persistence.
- Dependencies and integration points: Depends on `mantis_common.h` for `struct mantis_hwconfig` and on DVB frontend types where voltage callback is declared.
- Risks: Incorrect IDs or missing extern declarations would prevent board matching or link-time resolution.
- Test signals: Compile coverage and PCI ID probe tests for the board.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp3030.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/Kconfig -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/Kconfig

- Purpose: Kconfig entry for the Digiteq Automotive MGB4 V4L2 PCIe grabber/output driver.
- Important APIs/types/functions: `config VIDEO_MGB4` tristate with dependencies on V4L2, PCI, I2C, DMA, SPI, MTD, IIO, COMMON_CLK, and selects vb2 DMA-SG, IIO buffer support, Xilinx I2C/SPI, SPI NOR, and XDMA.
- Control flow: When enabled, Kbuild can build the module and automatically pull required support drivers.
- State and persistence: No runtime state; controls build-time configuration.
- Dependencies and integration points: Integrates media, DMAengine/XDMA, IIO, SPI NOR, MTD, and common clock subsystems.
- Risks: Missing dependencies would produce unresolved symbols or a module that probes without required child controllers. Broad selects increase kernel footprint.
- Test signals: Kconfig dependency resolution, `modpost`, and build tests with `VIDEO_MGB4=m/y`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/Makefile -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/Makefile

- Purpose: Build recipe for the MGB4 kernel module.
- Important APIs/types/functions: `mgb4-objs` lists register, core, vin, vout, sysfs, I2C, CMT, trigger, and DMA objects; `obj-$(CONFIG_VIDEO_MGB4)` emits `mgb4.o`.
- Control flow: Kbuild links the listed objects into one module when the Kconfig symbol is enabled.
- State and persistence: No runtime state.
- Dependencies and integration points: Depends on object filenames matching the source tree and Kconfig symbol.
- Risks: Omitting an object silently removes functionality at link time or causes unresolved symbols.
- Test signals: Kernel build and module link tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_cmt.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_cmt.c

- Purpose: Programs FPGA Clock Management Tile register tables for supported input frequency ranges and output pixel clocks.
- Important APIs/types/functions: Large precomputed `cmt_vals_out`, `cmt_vals_in`, address tables, `cmt_freq`, `freq_srch()`, `mgb4_cmt_set_vout_freq()`, and `mgb4_cmt_set_vin_freq_range()`.
- Control flow: Output configuration chooses nearest supported frequency, gates output config, asserts CMT programming bit, writes the selected table to CMT registers, deasserts programming bit, and restores config. Input range programming selects one of two tables with `array_index_nospec` and writes input CMT registers similarly.
- State and persistence: CMT register state persists in FPGA until reprogrammed/reset; `voutdev->freq` and `vindev->freq_range` track chosen values in RAM.
- Dependencies and integration points: Called by vout FPGA init and output `pclk_frequency` sysfs store, and by input `frequency_range` sysfs store.
- Risks: Nearest-frequency selection can surprise users requesting unsupported clocks. Tables are magic hardware data; any bad entry can break video timing. Reprogramming while queues run is guarded by callers, not the CMT functions themselves.
- Test signals: Test sysfs pclk/frequency_range writes, nearest-frequency reporting, video lock over supported clock range, and concurrent queue-start rejection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_cmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_cmt.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_cmt.h

- Purpose: Declaration header for MGB4 CMT programming helpers.
- Important APIs/types/functions: `mgb4_cmt_set_vout_freq` and `mgb4_cmt_set_vin_freq_range` with vin/vout type includes.
- Control flow: Used by vout init/sysfs and vin sysfs to program clocking.
- State and persistence: No state; functions mutate hardware registers and endpoint fields.
- Dependencies and integration points: Integrates CMT code with vin/vout modules.
- Risks: Includes both vin and vout headers, so include-order cycles must stay benign.
- Test signals: Compile plus sysfs frequency tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_cmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_core.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_core.c

- Purpose: Main MGB4 PCI driver: enables the device, creates XDMA/I2C/SPI child devices, maps registers, detects module/firmware type, and creates V4L2/IIO/sysfs/debugfs endpoints.
- Important APIs/types/functions: `mgb4_probe`, `mgb4_remove`, `init_xdma/free_xdma`, `init_i2c/free_i2c`, `init_spi/free_spi`, module-version and serial helpers, hwmon callbacks, and PCI ID table.
- Control flow: Probe enables PCIe features, allocates MSI-X vectors, sets 64-bit DMA mask, registers XDMA and DMA channels, maps video/CMT BAR windows, initializes SPI flash and xiic I2C, adds PCI sysfs and optional hwmon/debugfs, reads serial from MTD, detects module version through I2C and validates firmware type, then creates input/output V4L2 devices and trigger. Remove unwinds devices, groups, maps, channels, IRQs, and PCI state.
- State and persistence: `struct mgb4_dev` holds all live device resources; persistent hardware data includes SPI NOR partitions and serial-number MTD contents. Module version is mirrored into FPGA register 0xD4.
- Dependencies and integration points: Integrates PCI/MSI-X, AMD XDMA platform device, DMAengine, xiic-i2c, Xilinx SPI, SPI NOR/MTD, hwmon, debugfs, V4L2 vin/vout, IIO trigger, and sysfs modules.
- Risks: Probe tolerates missing expansion module to allow flashing, so later code must handle absent video devices. Partial failures in vin/vout creation are not fatal and may leave fewer endpoints. Error paths must match ownership exactly; `pci_disable_msix` is used after vector allocation.
- Test signals: Build and probe on T100/T200 IDs, no-module flashing mode, module/firmware mismatch, MTD serial read, hwmon temperature read, and remove after partially created endpoints.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_core.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_core.h

- Purpose: Central MGB4 constants, module-type predicates, DMA channel descriptor, and device state structure.
- Important APIs/types/functions: `MGB4_HW_FREQ`, device counts, `MGB4_IS_*` and `MGB4_HAS_VOUT` macros, `struct mgb4_dma_channel`, and `struct mgb4_dev`.
- Control flow: All MGB4 modules include this to share the detected module type, register mappings, child devices, V4L2 endpoint pointers, DMA channels, flash metadata, trigger, hwmon, and reconfiguration bit.
- State and persistence: `struct mgb4_dev` owns volatile kernel resources and names for persistent flash partitions; `io_reconfig` serializes cross-endpoint source changes.
- Dependencies and integration points: Couples core, DMA, I2C, regs, vin/vout, sysfs, trigger, SPI/MTD, clock, and hwmon code.
- Risks: Module-type macros encode hardware policy in bit shifts; future module versions need updates. Shared pointers require careful remove ordering.
- Test signals: Compile coverage plus probe tests for FPDL3, GMSL1, GMSL3, GMSL3C, and no-module cases.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_dma.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_dma.c

- Purpose: DMAengine wrapper around AMD XDMA channels for frame transfers between FPGA queues and vb2 scatter-gather buffers.
- Important APIs/types/functions: `mgb4_dma_transfer()`, `mgb4_dma_channel_init()`, `mgb4_dma_channel_free()`, and callback `chan_irq()`.
- Control flow: Channel init requests named `c2hN` and `h2cN` DMA channels and initializes completions. Transfer configures direction and device address, prepares SG transfer, sets completion callback, submits, issues pending, waits up to 10 seconds, and terminates on timeout. Free releases channels.
- State and persistence: Per-channel `dma_chan` and `completion` live in `struct mgb4_dev`; no persistence.
- Dependencies and integration points: Used by vin/vout workqueues for every captured/output frame; depends on XDMA platform device and DMAengine slave SG support.
- Risks: Completion is not reinitialized before each transfer, so a previously completed channel can make later waits return immediately unless DMAengine guarantees completion state is reset elsewhere. Timeout is coarse; error handling maps many failures to `-EIO`. Partial channel-init failure does not release earlier channels before returning.
- Test signals: Stress capture/output DMA, timeout injection, repeated transfers on one channel, partial channel request failure, and unload after DMA errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_dma.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_dma.h

- Purpose: Public MGB4 DMA channel lifecycle and transfer declarations.
- Important APIs/types/functions: `mgb4_dma_channel_init`, `mgb4_dma_channel_free`, and `mgb4_dma_transfer`.
- Control flow: Core initializes/frees channels; vin/vout call transfer from workqueues.
- State and persistence: No state; operates on `struct mgb4_dev` DMA channel arrays.
- Dependencies and integration points: Depends on `mgb4_core.h` and scatter-gather table types from kernel headers.
- Risks: Prototype changes affect core and both video directions.
- Test signals: Compile/link plus vin/vout streaming tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_i2c.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_i2c.c

- Purpose: Helper layer for serializer/deserializer I2C access with either 8-bit SMBus registers or 16-bit register-address transfers.
- Important APIs/types/functions: `mgb4_i2c_init/free`, `mgb4_i2c_read_byte`, `mgb4_i2c_write_byte`, `mgb4_i2c_mask_byte`, `mgb4_i2c_configure`, and internal `read_r16/write_r16`.
- Control flow: Init creates an I2C client for a board-info address and stores address width. Read/write dispatch to SMBus byte ops for 8-bit devices or custom two-byte register prefix messages for 16-bit devices. Mask helper read-modify-writes unless mask is full; configure applies register-value arrays.
- State and persistence: State is an `i2c_client` pointer and address width in endpoint structs; serializer/deserializer registers are persistent only until chip reset.
- Dependencies and integration points: Used by core module detection, vin deserializer init/sysfs, and vout serializer init/sysfs. Protected by `mgbdev->i2c_lock` at call sites that need bus serialization.
- Risks: 16-bit write buffer supports only two payload bytes beyond address; current byte writes fit. Callers must hold locks consistently. `mgb4_i2c_free` assumes a valid client.
- Test signals: Test 8-bit FPDL/GMSL1 and 16-bit GMSL3 devices, NACK handling, masked writes, and configuration arrays.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_i2c.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_i2c.h

- Purpose: Defines MGB4 I2C client wrapper and register-value configuration API.
- Important APIs/types/functions: `struct mgb4_i2c_client`, `struct mgb4_i2c_kv`, and helper prototypes.
- Control flow: Vin/vout/core create wrappers for extender, deserializer, and serializer chips and use keyed register arrays for setup.
- State and persistence: State is limited to the Linux I2C client pointer and address-size selector.
- Dependencies and integration points: Integrated with Linux I2C core and MGB4 sysfs/configuration modules.
- Risks: Address size is an int convention, not an enum; invalid values fall into 16-bit path.
- Test signals: Compile and serializer/deserializer register tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_io.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_io.h

- Purpose: Shared video I/O constants and helpers for MGB4 vin/vout queue code.
- Important APIs/types/functions: `MGB4_ERR_*` sentinel addresses, `MGB4_PERIOD`, `struct mgb4_frame_buffer`, `to_frame_buffer`, `has_yuv_and_timeperframe`, `pixel_size`.
- Control flow: Vin/vout use sentinels to detect FPGA frame-queue errors, period macro for timeperframe timers, frame-buffer wrapper for vb2 lists, and pixel-size helper for timing-derived frame periods.
- State and persistence: No state; helpers inspect video status register and timing structures.
- Dependencies and integration points: Depends on V4L2/vb2, math64, and MGB4 register access.
- Risks: Sentinel comparison assumes valid FPGA addresses never overlap high error values. `has_yuv` and `has_timeperframe` are tied to one status bit.
- Test signals: Compile plus streaming tests that force queue empty/full/timeout status and YUV capability detection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_regs.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_regs.c

- Purpose: Resource mapping helpers for MGB4 MMIO register windows.
- Important APIs/types/functions: `mgb4_regs_map()` and `mgb4_regs_free()`.
- Control flow: Map requests a memory region, ioremaps it, and records base/size; free unmaps and releases the region.
- State and persistence: State is `struct mgb4_regs` mapbase/mapsize/membase; no persistence.
- Dependencies and integration points: Used by core to map video and CMT windows before all register access.
- Risks: Free assumes a successfully mapped resource. Error handling returns `-EINVAL` for both busy region and ioremap failure.
- Test signals: Probe failure injection for busy BAR subregion and ioremap failure, plus unload map cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_regs.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_regs.h

- Purpose: Defines the MGB4 register mapping object and basic 32-bit MMIO helpers.
- Important APIs/types/functions: `struct mgb4_regs`, `mgb4_write_reg`, `mgb4_read_reg`, `mgb4_mask_reg`, map/free prototypes.
- Control flow: All MGB4 modules access FPGA registers through this wrapper; mask helper performs read-modify-write.
- State and persistence: State is the mapped MMIO pointer and resource metadata.
- Dependencies and integration points: Depends on Linux `io.h`; integrated across core, CMT, sysfs, vin/vout, trigger, hwmon.
- Risks: Read-modify-write is not internally locked, so callers must serialize shared registers. Macro names evaluate arguments directly.
- Test signals: Compile plus concurrent sysfs/streaming register access tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs.h

- Purpose: Declares attribute arrays for PCI card, input, and output sysfs groups selected by module type.
- Important APIs/types/functions: `mgb4_pci_attrs`, `mgb4_fpdl3_in_attrs`, `mgb4_gmsl3_in_attrs`, `mgb4_gmsl1_in_attrs`, `mgb4_fpdl3_out_attrs`, `mgb4_gmsl3_out_attrs`, `mgb4_gmsl1_out_attrs`.
- Control flow: Core and vin/vout create device groups using generated `ATTRIBUTE_GROUPS` around these arrays.
- State and persistence: No state; attribute handlers live in sysfs implementation files.
- Dependencies and integration points: Connects core/vin/vout registration with sysfs files.
- Risks: Missing NULL-terminated arrays or wrong module selection would expose wrong knobs.
- Test signals: Probe and sysfs enumeration tests for each module type.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_in.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_in.c

- Purpose: Input-video sysfs interface for MGB4 status and deserializer/FPGA configuration.
- Important APIs/types/functions: Common attributes include input id, OLDI lane width, color mapping, link/stream status, resolution, sync status/gaps, pixel clock, porch widths, and frequency range; FPDL3 adds input width; GMSL adds mode, stream id, and FEC.
- Control flow: Show handlers read FPGA registers and deserializer registers. Store handlers parse numeric values, validate ranges, update FPGA bits and/or I2C registers, sometimes reset links. Frequency range and stream ID changes lock the video device and reject busy queues; live-safe changes intentionally skip queue locks.
- State and persistence: State updated includes FPGA config/sync registers, `vindev->freq_range`, and deserializer registers. No disk persistence.
- Dependencies and integration points: Used by `mgb4_vin_create()` via module-specific attribute groups; depends on MGB4 I2C, CMT, video locks, and module-type macros.
- Risks: Live configuration writes can disrupt active signals by design. Some multi-register I2C updates OR errors together and return generic `-EIO`. The code checks FPGA/I2C lane-width consistency and returns errors if they drift.
- Test signals: Test every sysfs attribute per FPDL3/GMSL1/GMSL3, invalid values, busy queue rejection, live link reset behavior, and consistency after replug or firmware reset.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_in.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_out.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_out.c

- Purpose: Output-video sysfs interface for MGB4 source routing, display timings, pixel clock, color mapping, polarities, and serializer settings.
- Important APIs/types/functions: Helpers `loopin_cnt()` and `is_busy()`, show/store handlers for output id, video source, color mapping, display width/height, frame rate, sync widths/porches/polarities, FPDL3 output width, and pclk frequency; module-specific attr arrays.
- Control flow: Video-source changes use a global `io_reconfig` bit, check all vin/vout queues for busy state, enable/disable loopback input queues as needed, and update output source/config bits. Timing stores update FPGA registers, many live-safe; dimensions and pclk lock the vdev and reject busy queues. Pclk calls CMT programming and may update FPDL3 serializer double-pixel mode.
- State and persistence: State includes output FPGA registers, `voutdev->freq`, serializer registers, and loopback enable bits. No disk persistence.
- Dependencies and integration points: Used by `mgb4_vout_create()` through module-specific groups; coordinates with vin loopback behavior and CMT/I2C helpers.
- Risks: Cross-device reconfiguration is subtle and intentionally avoids taking all locks simultaneously. Existing streaming blocks source changes, but live timing writes can affect displayed output. Serializer-free on module types without serializer client may depend on zeroed client state.
- Test signals: Test source switching among self-output and both inputs, busy rejection while any queue runs, loopback capture continuity, pclk rounding/double-pixel handling, and all invalid sysfs values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_pci.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_pci.c

- Purpose: PCI-device sysfs attributes exposing module type/version, firmware type/version, and serial number.
- Important APIs/types/functions: Show handlers for `module_version`, `module_type`, `fw_version`, `fw_type`, `serial_number`; `mgb4_pci_attrs`.
- Control flow: Handlers read `mgbdev` from device driver data and return cached module/serial values or video register 0xC4 fields.
- State and persistence: Serial number is read once from MTD by core; firmware/module fields reflect detected hardware or live FPGA register.
- Dependencies and integration points: Added by `mgb4_core.c` to the PCI device.
- Risks: If no module is present, values may remain zero/unknown but attributes still exist. Serial formatting assumes a four-byte packed decimal-ish value.
- Test signals: Read sysfs files after probe, no-module mode, and failed serial MTD read.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_trigger.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_trigger.c

- Purpose: Creates an IIO triggered-buffer device for MGB4 external/video-synchronized trigger events.
- Important APIs/types/functions: Private `struct trigger_data`, `trigger_read_raw`, `trigger_set_state`, `trigger_handler`, `probe_trigger`, `remove_trigger`, `mgb4_trigger_create`, and `mgb4_trigger_free`.
- Control flow: Create allocates an IIO device, sets channel metadata, allocates/registers an IIO trigger on XDMA user IRQ 11, sets up triggered buffer, and registers the device. Trigger state toggles the user IRQ. Handler reads event register 0xA0, acknowledges it, pushes data plus timestamp to buffers, notifies trigger done, and clears IRQ in register 0xB4.
- State and persistence: Stores IIO trigger pointer and parent `mgbdev` in IIO private data; event register state is volatile hardware state.
- Dependencies and integration points: Integrated with core probe/remove, XDMA user IRQs, Linux IIO trigger and buffer frameworks.
- Risks: IRQ 11 is shared by assumption with hardware event source. Raw reads are blocked while buffers are enabled. Correct cleanup order matters for trigger, IRQ, buffer, and IIO device.
- Test signals: Test raw read, triggered buffer capture, enabling/disabling trigger, timestamp/data correctness, and remove while buffer is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_trigger.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_trigger.h

- Purpose: Declaration header for MGB4 IIO trigger lifecycle.
- Important APIs/types/functions: `mgb4_trigger_create` and `mgb4_trigger_free`.
- Control flow: Core calls create after video endpoints and free before endpoint removal.
- State and persistence: No state; lifecycle functions own an `iio_dev` returned to core.
- Dependencies and integration points: Depends on IIO types and `struct mgb4_dev` visibility from including files.
- Risks: No include guard is present, so duplicate inclusion could redeclare prototypes only; harmless but inconsistent.
- Test signals: Compile and probe/remove tests with IIO enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_trigger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vin.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vin.c

- Purpose: Implements MGB4 V4L2 capture devices: deserializer setup, signal timing detection, vb2 queues, DMA completion, source-change events, debugfs, sysfs groups, and loopback cooperation.
- Important APIs/types/functions: Configuration tables for two inputs, deserializer I2C arrays, V4L2 timing cap, queue ops, file ops, ioctl ops, `dma_transfer`, `signal_change`, IRQ handlers, `deser_init`, `fpga_init`, `mgb4_vin_create`, and `mgb4_vin_free`.
- Control flow: Create allocates an endpoint, initializes buffer list/work, requests frame and error IRQs, initializes FPGA and deserializer, registers V4L2/vb2 video node, enables signal-change IRQ, adds sysfs and debugfs. Open snapshots current timings or defaults to 1080p60. Stream-on enables FPGA queue unless loopback already keeps it running, writes padding, and enables frame IRQ. Frame IRQ schedules DMA work to pull one FPGA frame address into the next vb2 buffer. Error IRQ schedules source-change work and may mark streaming queue errored on resolution change. Stream-off disables IRQ/queue, cancels work, clears padding, and returns buffers.
- State and persistence: State includes `timings`, `freq_range`, `padding`, sequence, buffer list, deserializer client, work items, and FPGA registers. No disk persistence.
- Dependencies and integration points: Depends on V4L2/vb2 DMA-SG, XDMA user IRQs, MGB4 DMA/CMT/I2C/sysfs/io helpers, deserializer chips, and vout loopback state.
- Risks: Loopback requires capture queue hardware to remain enabled even without V4L2 streaming. Buffer list access uses spinlock but start_streaming removes first buffer in vout only; vin DMA handles empty lists gracefully. Timing changes while streaming call queue error but userspace must recover. Partial create errors after deserializer init do not free the I2C client on all paths.
- Test signals: Test capture formats ABGR/YUYV, DV timings query/set, no-signal behavior, IRQ-driven source-change events, stream start/stop, loopback padding, DMA errors, and remove during active capture.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vin.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vin.h

- Purpose: Data structures and lifecycle declarations for one MGB4 video input endpoint.
- Important APIs/types/functions: `struct mgb4_vin_regs`, `struct mgb4_vin_config`, `struct mgb4_vin_dev`, `mgb4_vin_create`, and `mgb4_vin_free`.
- Control flow: Implementation uses config register offsets and IRQ/channel IDs to create each input; other modules use `mgbdev->vin[]` pointers for loopback and sysfs coordination.
- State and persistence: Endpoint state includes V4L2/vb2 objects, locks, buffer list, works, timings, frequency range, padding, deserializer client, config pointer, and debugfs register metadata.
- Dependencies and integration points: Integrated by core, vout loopback, input sysfs, CMT, and DMA code.
- Risks: Any struct layout change affects multiple modules. Debugfs register array sizing assumes `mgb4_vin_regs` is only 32-bit fields.
- Test signals: Compile plus capture endpoint creation/free tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vout.c -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vout.c

- Purpose: Implements MGB4 V4L2 output devices: serializer setup, timing programming, vb2 output queues, DMA writes to FPGA frame queues, loopback exclusion, sysfs/debugfs, and endpoint lifecycle.
- Important APIs/types/functions: Configuration tables for two outputs, serializer I2C arrays, V4L2 timing cap, queue/file/ioctl ops, `dma_transfer`, output IRQ `handler`, `ser_init`, `fpga_init`, `mgb4_vout_create`, and `mgb4_vout_free`.
- Control flow: Create allocates endpoint, requests output IRQ, initializes FPGA defaults and serializer, registers V4L2/vb2 output node, adds sysfs/debugfs. Open rejects devices whose source is loopback input rather than self-output, then snapshots current resolution. Stream-on writes padding, enables FPGA output queue, primes first frame by DMA to the current FPGA address, and enables IRQ. IRQ schedules DMA work for subsequent queued buffers. Stream-off disables IRQ/hardware, cancels work, clears padding, and returns buffers.
- State and persistence: State includes width, height, pixel clock, padding, buffer list, serializer client, V4L2/vb2 objects, and FPGA registers. No disk persistence.
- Dependencies and integration points: Depends on V4L2/vb2 DMA-SG, XDMA user IRQs, MGB4 DMA/CMT/I2C/sysfs/io helpers, and vin loopback source selection.
- Risks: Open-time loopback check prevents V4L2 output while hardware loopback uses the output. `start_streaming()` assumes at least one queued buffer due to vb2 minimum but direct list access is sensitive. Freeing serializer on GMSL3/no-serializer paths may need valid-client checks.
- Test signals: Test output streaming/write/MMAP/DMABUF, source loopback EBUSY, pclk/timing changes, DMA queue sentinel errors, underrun behavior, and unload during active output.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vout.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vout.h

- Purpose: Data structures and lifecycle declarations for one MGB4 video output endpoint.
- Important APIs/types/functions: `struct mgb4_vout_regs`, `struct mgb4_vout_config`, `struct mgb4_vout_dev`, `mgb4_vout_create`, and `mgb4_vout_free`.
- Control flow: Core creates outputs when module type supports them; sysfs and vin loopback code inspect and mutate output device state.
- State and persistence: Endpoint state includes V4L2/vb2 objects, locks, buffer list, DMA work, width/height/frequency/padding, serializer client, config pointer, and debugfs register metadata.
- Dependencies and integration points: Integrated with core, sysfs_out, CMT, DMA, and vin loopback helpers.
- Risks: Struct fields are shared across modules without accessors, so changes require synchronized updates. Debugfs array sizing assumes only 32-bit register fields.
- Test signals: Compile plus output endpoint creation/free and loopback tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/Kconfig -->

# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/Kconfig

- Purpose: Kconfig entry for NetUP Universal DVB PCIe card support.
- Important APIs/types/functions: `config DVB_NETUP_UNIDVB` depends on DVB core, V4L2, PCI, I2C, SPI master; selects videobuf2 DVB/vmalloc and optional frontend/tuner/LNB helpers under autoselect.
- Control flow: Controls building a driver for dual-stream DVB-S/S2/T/T2/C/C2 cards with two CI slots.
- State and persistence: No runtime state; build-time only.
- Dependencies and integration points: Integrates PCI DVB bridge code with frontend subdrivers and SPI/I2C support.
- Risks: Autoselect choices must match hardware revisions; missing frontend modules break tuning though core may build.
- Test signals: Kconfig build matrix with `MEDIA_SUBDRV_AUTOSELECT` on/off and module link tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/Makefile -->

# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/Makefile

- Purpose: Build recipe for the NetUP Universal DVB driver.
- Important APIs/types/functions: `netup-unidvb-objs` includes core, I2C, CI, and SPI objects; `obj-$(CONFIG_DVB_NETUP_UNIDVB)` builds the module; `ccflags-y` adds DVB frontend include path.
- Control flow: Kbuild links the multi-object module when enabled.
- State and persistence: No runtime state.
- Dependencies and integration points: Depends on source file names and frontend headers in `drivers/media/dvb-frontends`.
- Risks: Object omission would remove interrupts/I2C/CI/SPI functionality or fail linking.
- Test signals: Kernel build and modpost tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb.h -->

# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb.h

- Purpose: Shared definitions for the NetUP Universal Dual DVB-CI PCIe driver.
- Important APIs/types/functions: Driver/version/vendor constants, IRQ register offsets and bits, hardware revision enum, `struct netup_dma`, `enum netup_i2c_state`, `struct netup_i2c`, `struct netup_ci_state`, `struct netup_unidvb_dev`, and prototypes for I2C/CI/SPI helpers.
- Control flow: Core code maps MMIO, allocates DMA, registers two frontends, initializes two I2C controllers, CI slots, SPI, and dispatches interrupts to the declared handlers. DMA structs combine ring buffers, work, timeout, and register pointers; I2C state machine uses wait queues and spinlocks.
- State and persistence: Device state includes PCI coordinates, MMIO windows, DMA memory, frontend arrays, workqueue, DMA/I2C/CI/SPI state, and hardware revision. No file persistence in this header.
- Dependencies and integration points: Integrates Linux PCI, I2C, workqueues, videobuf2 DVB, V4L2 device/common, DVB CA EN50221, and companion core/I2C/CI/SPI source files.
- Risks: Shared state is interrupt-heavy: DMA ring, I2C state, CI status, and SPI IRQs need careful locking. Hardware revision constants select different frontend stacks elsewhere.
- Test signals: Compile all companion objects, probe both hardware revisions, exercise DMA IRQs, I2C transfers, CAM interrupts, and SPI initialization/release.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb.h -->
