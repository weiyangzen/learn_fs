# Research Group subset-b-001082

Source-tree-aligned grouped research for subset B work item `subset-b-001082`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/xen-tpmfront.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/xen-tpmfront.c

Purpose: Xen frontend for a virtual TPM device. It exposes a Xen vTPM backend through the Linux TPM class by creating a shared page ring, grant reference, event channel, and `tpm_chip` whose class operations copy TPM commands/results through the Xen `vtpm_shared_page` protocol.

Important APIs/types/functions: `struct tpm_private` owns the Xenbus device, TPM chip, shared page, event channel, grant reference, IRQ, and read waitqueue. `wait_for_tpm_stat()` implements IRQ-backed or polling TPM status waits with freezer-aware signal handling. `vtpm_status()`, `vtpm_send()`, `vtpm_recv()`, and `vtpm_cancel()` are the `tpm_class_ops`. `setup_ring()` publishes `ring-ref`, `event-channel`, and `feature-protocol-v2` in Xenstore; `tpmfront_probe()`, `tpmfront_remove()`, `tpmfront_resume()`, and `backend_changed()` implement the Xenbus lifecycle.

Control flow: probe allocates private state, allocates a managed TPM chip, maps one shared page with a grant reference, allocates and binds an event channel IRQ, publishes the frontend ring details to Xenstore, moves to `Initialised`, gets TPM timeouts, and registers the chip. A TPM command waits for `VTPM_STATE_IDLE`, copies the request after the shared-page header and extra-page array, sets `length` and `VTPM_STATE_SUBMIT`, notifies the backend, waits for completion based on the TPM ordinal duration, and leaves result retrieval to `vtpm_recv()`. The IRQ handler wakes waiters only for `IDLE` and `FINISH` states. Backend state changes require protocol v2 before switching to `Connected`; close states unregister the device.

State and persistence: all state is runtime-only Xen frontend state. The shared page carries backend-visible `state`, `length`, and data; cancellation is represented by writing `VTPM_STATE_CANCEL` and notifying. Suspend/resume tears down and reprobes the frontend because in-flight vTPM commands are considered interrupted.

Dependencies and integration: depends on Xen PV device support, Xenbus, Xen grant tables, Xen event channels, TPM core helpers, and `xen/interface/io/tpmif.h`. It integrates with the generic TPM class rather than exposing its own character device.

Risks: shared-page offset and length validation is critical because data must fit in a single page after any `extra_pages` metadata. Timeout and signal paths collapse several failures to `-ETIME` and issue cancellation, so backend races around `CANCEL`, `IDLE`, and `FINISH` are subtle. `tpmfront_remove()` assumes TPM chip drvdata relationships are intact. Resume destroys the previous frontend, so missed unregister/free sequencing would leak event channels or grants.

Test signals: boot a Xen guest with a vTPM backend and verify `/dev/tpm*` registration, Xenstore `feature-protocol-v2`, event-channel interrupt completion, TPM selftests/known commands, timeout cancellation, backend disconnect, and suspend/resume or migration with an in-flight command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/xen-tpmfront.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ttyprintk.c -->
# sources/distributed-fs/ceph-client/drivers/char/ttyprintk.c

Purpose: Implements the `ttyprintk` pseudo TTY that lets userspace write lines into the kernel log with a configured printk priority and `[U]` prefix. It is useful for boot/service logging where userspace console messages should be interleaved with kernel messages.

Important APIs/types/functions: `struct ttyprintk_port` embeds `tty_port` plus a spinlock. `tpk_printk()` normalizes CR/LF handling, fragments overlong lines, and buffers partial lines. `tpk_flush()` emits the current line with `printk(TPK_PREFIX "[U] ...")`. `tpk_open()`, `tpk_close()`, `tpk_write()`, `tpk_write_room()`, `tpk_hangup()`, and `tpk_port_shutdown()` implement the TTY operations. `ttyprintk_console_device()` lets the registered console point at the tty driver.

Control flow: init allocates a one-line raw unnumbered TTY driver at `TTYAUX_MAJOR` minor 3, initializes and links the single tty port, registers the driver, and registers a console named `ttyprintk`. Writes take the port spinlock, feed bytes through `tpk_printk()`, flush on newline/CR or line-size overflow, and return the original count. Port shutdown flushes any trailing partial line.

State and persistence: global runtime state is the singleton `tpk_port`, `tpk_curr`, `tpk_buffer`, and `ttyprintk_driver`. Buffered partial text persists only until newline, overflow fragmentation, shutdown, or module exit.

Dependencies and integration: depends on the Linux TTY core, console registration, printk, and `CONFIG_TTY_PRINTK_LEVEL` for log priority. The device appears as a console-type TTY rather than a normal misc device.

Risks: `tpk_buffer` and `tpk_curr` are global for the single port, so locking must continue to cover all write/flush paths. Long-line fragmentation appends a backslash and flushes, which changes exact user text. `write_room()` advertises 4 KiB independent of the internal line buffer, relying on immediate formatting. Init error cleanup must destroy the tty port after driver allocation failures.

Test signals: open `/dev/ttyprintk`, write LF, CR, CRLF, partial lines, and lines longer than `TPK_STR_SIZE`; verify printk priority and `[U]` prefix, no interleaving under concurrent writes, flush on close/shutdown, and device/console registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ttyprintk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/uv_mmtimer.c -->
# sources/distributed-fs/ceph-client/drivers/char/uv_mmtimer.c

Purpose: SGI UV platform misc character device exposing the UV real-time clock as `/dev/mmtimer`. It provides ioctls for resolution, frequency, counter width/current value, and supports read-only mmap of the hardware RTC page.

Important APIs/types/functions: `uv_mmtimer_ioctl()` handles `MMTIMER_GETOFFSET`, `MMTIMER_GETRES`, `MMTIMER_GETFREQ`, `MMTIMER_GETBITS`, `MMTIMER_MMAPAVAIL`, and `MMTIMER_GETCOUNTER`. `uv_mmtimer_mmap()` maps the UV local MMR RTC page with noncached page protection. `uv_mmtimer_init()` validates UV hardware and clock frequency, computes femtosecond period, and registers a `miscdevice`.

Control flow: module init rejects non-UV systems and invalid `sn_rtc_cycles_per_second`, computes `(1e15 + freq/2) / freq`, registers the misc device, and logs version/frequency. Ioctl requests either return scalar values directly or copy frequency/resolution/counter values to userspace. `MMTIMER_GETOFFSET` returns zero for hub rev 1 or a cacheline-based per-processor offset for replicated RTC pages. mmap accepts exactly one read-only page, forces noncached mapping, aligns `UV_LOCAL_MMR_BASE | UVH_RTC`, and calls `remap_pfn_range()`.

State and persistence: only `uv_mmtimer_femtoperiod` and the misc registration are stored by the driver. The actual counter and frequency live in UV platform firmware/MMR state and are not persisted by this module.

Dependencies and integration: depends on x86 SGI UV platform headers, `is_uv_system()`, `uv_local_mmr_address()`, `uv_get_min_hub_revision_id()`, `uv_blade_processor_id()`, `sn_rtc_cycles_per_second`, miscdevice, mmap, and mmtimer ioctl ABI.

Risks: this is hardware-specific and returns generic `-1` rather than specific errno from init failures. mmap assumes the UV RTC physical mapping and rejects large pages over 64 KiB. Userspace sees raw hardware timing state, so counter width/frequency correctness depends on firmware values. Writeable mappings must remain rejected.

Test signals: boot on UV hardware, verify `/dev/mmtimer`, ioctl frequency/resolution/bit count/counter values, offset behavior across hub revisions and CPUs, read-only mmap success for one page, mmap rejection for wrong length/write flags, and failure on non-UV systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/uv_mmtimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/virtio_console.c -->
# sources/distributed-fs/ceph-client/drivers/char/virtio_console.c

Purpose: Virtio console, virtio port, and remoteproc serial driver. It creates `/dev/vport<device>p<port>` character devices for generic ports and attaches console ports to the hvc console layer, while handling virtio multiport control messages, virtqueues, hotplug, resize, suspend/resume, and debug/sysfs reporting.

Important APIs/types/functions: `struct ports_driver_data` tracks all devices and console ports; `struct ports_device` owns virtio queues, control work, config work, port list, and char major; `struct port` owns per-port queues, cdev/device, hvc console state, waitqueue, async queue, connection flags, and byte stats; `struct port_buffer` wraps DMA or scatterlist buffers. Key paths include `alloc_buf()`/`free_buf()`/`reclaim_dma_bufs()`, `add_inbuf()`/`get_inbuf()`/`fill_queue()`, `__send_control_msg()`, `__send_to_port()`, `port_fops_*()`, `init_port_console()`, `add_port()`, `unplug_port()`, `handle_control_message()`, queue callbacks, `init_vqs()`, `virtcons_probe()`, `virtcons_remove()`, `virtcons_freeze()`, and `virtcons_restore()`.

Control flow: probe validates config access, allocates a `ports_device`, registers a per-device char major, reads multiport capacity if available, initializes locks/work, discovers virtqueues, marks the virtio device ready, fills the control receive queue for multiport or creates legacy port 0, links the device globally, and sends `DEVICE_READY`. Control queue work consumes host packets for add/remove/console/resize/open/name events and then requeues control buffers. Data RX interrupts fetch an input buffer, optionally discard data for closed generic ports, wake readers and hvc, and send SIGIO. Writes wait for host connectivity and free queue space, allocate a DMA buffer, copy userspace data or splice pages into an SG list, enqueue it on the out virtqueue, kick the host, and reclaim completed buffers later. HVC `put_chars()` uses a synchronous spin-wait send path; `get_chars()` drains the same input buffers without userspace copy.

State and persistence: state is runtime virtio device state: per-port `guest_connected`, `host_connected`, `outvq_full`, `inbuf`, names, debug stats, hvc vterm numbers, DMA buffers pending deferred free, and virtqueue contents. Port names become sysfs attributes but are not persisted by the driver. Freeze resets virtio queues, clears host connection state, removes buffered data, and restore rebuilds queues and reannounces ports/open state.

Dependencies and integration: integrates with virtio IDs `VIRTIO_ID_CONSOLE` and optional `VIRTIO_ID_RPROC_SERIAL`, virtio console config/control ABI, hvc console APIs, Linux char devices/cdev, sysfs, debugfs, fasync/SIGIO, splice/pipe helpers, DMA mapping, workqueues, IDA, and PM sleep callbacks.

Risks: lifetime and hot-unplug are complex: open file references, cdev/device teardown, virtqueue removal, hvc references, and deferred DMA frees must not race. Control message send spins while holding the control output lock until the host consumes the buffer. The input path intentionally discards closed generic-port data but accepts console/rproc data, so connection flag mistakes alter user-visible semantics. Multiport queue indexing depends on `max_nr_ports` bounds. Splice uses page stealing/copy fallback and excludes remoteproc. Suspend/restore must rebuild per-port queue pointers exactly.

Test signals: run virtio-console in a VM with legacy and multiport hosts; add/remove ports dynamically; verify `/dev/vport*`, port names/sysfs uevents, debugfs counters, blocking and nonblocking read/write/poll, SIGIO, splice writes, host open/close HUP behavior, hvc console I/O and resize, rproc serial behavior, hot-unplug with open descriptors, module unload, and suspend/resume with ports open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/virtio_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/Makefile

Purpose: Kbuild fragment for the Xilinx HWICAP character driver.

Important APIs/types/functions: It builds `xilinx_hwicap_m.o` when `CONFIG_XILINX_HWICAP` is enabled and composes that module from `xilinx_hwicap.o`, `fifo_icap.o`, and `buffer_icap.o`.

Control flow: no runtime control flow; this file only declares object composition for the kernel build.

State and persistence: no runtime state. Build state is determined by Kconfig symbol selection.

Dependencies and integration: integrates the common char-device layer with both FIFO-backed and BRAM-buffer-backed ICAP transport implementations.

Risks: object ordering must continue to include both backend implementations because `xilinx_hwicap.c` references both config tables. The target name `xilinx_hwicap_m` controls the module object name and must match surrounding Kbuild expectations.

Test signals: build with `CONFIG_XILINX_HWICAP=y` and `=m`, verify all three objects link, and boot/probe a matching Device Tree node for both compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.c -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.c

Purpose: Implements the BRAM-buffer variant of the Xilinx HWICAP backend. It moves configuration/readback words between system memory and the ICAP core through a 2 KiB on-core storage buffer and polled control/status registers.

Important APIs/types/functions: Exports `buffer_icap_get_status()`, `buffer_icap_reset()`, `buffer_icap_set_configuration()`, and `buffer_icap_get_configuration()` for `struct hwicap_driver_config`. Helpers access BRAM words and registers: `buffer_icap_get_bram()`, `buffer_icap_set_bram()`, `buffer_icap_busy()`, `buffer_icap_set_size()`, `buffer_icap_set_offset()`, `buffer_icap_set_rnc()`, `buffer_icap_device_read()`, and `buffer_icap_device_write()`.

Control flow: writes copy input words into BRAM until the 512-word buffer fills, then program size/offset/direction, start configuration by writing RNC, and poll done with `XHI_MAX_RETRIES`; any transfer failure resets the core. Reads request chunks of up to 512 words from ICAP into BRAM, poll completion, then copy BRAM words to the caller. Status reads directly return the hardware status register; reset writes a magic value to the status register for internal core versions.

State and persistence: no private software state beyond hardware register and BRAM contents. The parent `hwicap_drvdata` serializes access and owns base address/device state.

Dependencies and integration: depends on big-endian MMIO accessors, `xilinx_hwicap.h` status masks/retry count, and the common `xilinx_hwicap.c` char-device read/write/open paths.

Risks: the transfer is fully polled with bounded retries, so slow hardware can produce `-EBUSY`. The buffer limit must be enforced on both offset and count. Comments for device read/write contain stale direction wording, so maintainers must trust register behavior rather than comments. Reset support differs across published core versions.

Test signals: on `xlnx,opb-hwicap-1.00.b`, write bitstream chunks larger and smaller than 2 KiB, perform register readback after a request packet, inject busy/timeout conditions if possible, verify DALIGN/status behavior, and test unaligned userspace byte writes through the parent driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.h -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.h

Purpose: Public internal header for the BRAM-buffer HWICAP backend.

Important APIs/types/functions: Declares `buffer_icap_set_configuration()`, `buffer_icap_get_configuration()`, `buffer_icap_get_status()`, and `buffer_icap_reset()` against `struct hwicap_drvdata`.

Control flow: no runtime control flow; it is a compile-time contract used by `xilinx_hwicap.c`.

State and persistence: no state.

Dependencies and integration: includes Linux type/cdev/platform headers, `asm/io.h`, and `xilinx_hwicap.h` for `struct hwicap_drvdata` and shared ICAP constants.

Risks: prototype drift breaks the `hwicap_driver_config` initializer in the common driver. Parameter names use legacy capitalization in comments/prototypes but types match the implementation.

Test signals: compile coverage with `CONFIG_XILINX_HWICAP` catches declaration/definition mismatches; runtime buffer backend tests exercise these exports indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.c -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.c

Purpose: Implements the FIFO-backed Xilinx HWICAP backend. It streams configuration and readback words through hardware write/read FIFOs, size/control/status registers, and polled occupancy/vacancy checks.

Important APIs/types/functions: Exports `fifo_icap_get_status()`, `fifo_icap_set_configuration()`, `fifo_icap_get_configuration()`, `fifo_icap_reset()`, and `fifo_icap_flush_fifo()`. Helpers wrap FIFO and control register operations: `fifo_icap_fifo_write()`, `fifo_icap_fifo_read()`, `fifo_icap_set_read_size()`, `fifo_icap_start_config()`, `fifo_icap_start_readback()`, `fifo_icap_busy()`, `fifo_icap_write_fifo_vacancy()`, and `fifo_icap_read_fifo_occupancy()`.

Control flow: write first rejects a busy ICAP, then repeatedly waits for write FIFO vacancy, pushes words, starts configuration after each filled burst, and finally waits for done. Read rejects busy ICAP, breaks requests into `XHI_MAX_READ_TRANSACTION_WORDS` chunks, programs read size, starts readback, waits for read FIFO occupancy, and drains words into the caller buffer. Reset toggles the software reset bit; flush toggles FIFO clear.

State and persistence: software state is only local loop counters; persistent state is in the ICAP hardware FIFOs/control registers. Parent driver locking serializes calls.

Dependencies and integration: used by `xilinx_hwicap.c` for Device Tree compatible `xlnx,xps-hwicap-1.00.a`. It relies on `xilinx_hwicap.h` status bits/retry count and big-endian MMIO accessors.

Risks: retry counters are shared across nested wait loops in each transfer and are not reset per FIFO wait, making very large or slow operations sensitive to `XHI_MAX_RETRIES`. `fifo_icap_set_configuration()` starts configuration after each FIFO fill and only reports `remaining_words` mismatch, so done-timeout paths require careful review. Interrupt registers are defined but the driver is purely polled.

Test signals: exercise FIFO backend configuration and readback, transfer sizes over FIFO depth and over the read-transaction limit, busy hardware rejection, timeout handling, reset/flush effects, and parent open/read/write byte-buffering paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.h -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.h

Purpose: Public internal header for the FIFO HWICAP backend.

Important APIs/types/functions: Declares `fifo_icap_get_configuration()`, `fifo_icap_set_configuration()`, `fifo_icap_get_status()`, `fifo_icap_reset()`, and `fifo_icap_flush_fifo()`.

Control flow: no runtime flow; this header supplies prototypes consumed by the common HWICAP module.

State and persistence: no state.

Dependencies and integration: includes the common `xilinx_hwicap.h` definitions and Linux/IO headers. `xilinx_hwicap.c` uses the declarations to populate `fifo_icap_config`.

Risks: declaration drift breaks the backend config table. `fifo_icap_flush_fifo()` is exported internally but not wired into the generic config vtable, so direct users must include this header.

Test signals: compile the HWICAP module and run FIFO-backend probe/read/write tests to cover the declared functions indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/xilinx_hwicap.c -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/xilinx_hwicap.c

Purpose: Common Xilinx HWICAP character-device driver. It exposes `/dev/icap0` for FPGA configuration/readback and selects either the BRAM-buffer or FIFO transport backend based on Device Tree compatible data.

Important APIs/types/functions: `hwicap_drvdata` instances are initialized by `hwicap_setup()`. `hwicap_command_desync()` and `hwicap_get_configuration_register()` construct ICAP packet sequences. `hwicap_initialize_hwicap()` resets, desynchronizes, reads IDCODE, and desynchronizes again on open. `hwicap_read()`, `hwicap_write()`, `hwicap_open()`, and `hwicap_release()` implement the character device. Probe chooses `config_registers` for Virtex2P/4/5/6 and a `hwicap_driver_config` for buffer or FIFO backends.

Control flow: module init registers class `xilinx_config`, reserves static major 259 for one device, and registers a platform driver. Probe reads optional `port-number` and `xlnx,family`, maps MMIO, initializes driver data and cdev, and creates `icapN`. Open is exclusive under global and per-device mutexes, initializes hardware, clears byte staging buffers, and marks `is_open`. Write combines leftover 1-3 bytes with userspace data, writes only full 32-bit words through the selected backend, and stores final incomplete bytes. Release pads any leftover write bytes with zeros, sends DESYNC, and clears open state. Read rounds requests up to words, reads whole words, returns bytes, and stores leftover bytes for the next read.

State and persistence: per-device runtime state includes open flag, read/write leftover byte buffers, cdev/devt, MMIO base, backend function table, and selected configuration-register layout. Global state tracks the single supported device slot. Hardware ICAP state can outlive open/close and is intentionally left desynchronized after release.

Dependencies and integration: depends on platform devices/OF, fixed char-device region, cdev/class device creation, `buffer_icap` and `fifo_icap` backends, Xilinx ICAP packet format constants, and userspace bitstream tooling that constructs valid packets.

Risks: the driver exposes powerful FPGA reconfiguration; writing an invalid or full bitstream can overwrite the running design. Only one device is supported and cleanup uses device/minor state that must match the registered devt. `hwicap_read()` has delicate word/byte-leftover handling and relies on userspace issuing readback packets first. Module init does not unregister the class if `register_chrdev_region()` fails. Release pads partial writes, which may alter malformed streams.

Test signals: probe both compatible strings and family variants, verify `/dev/icap0` exclusive open, IDCODE read during open, byte counts for unaligned writes/reads, DESYNC on release, rejection of second open, char-device cleanup on remove, and controlled partial-bitstream/readback operations on real or simulated ICAP hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/xilinx_hwicap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/xilinx_hwicap.h -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/xilinx_hwicap.h

Purpose: Shared internal ABI for the Xilinx HWICAP driver and both backend implementations. It defines driver state, backend operation table, configuration register numbering, packet constructors, command constants, and status masks.

Important APIs/types/functions: `struct hwicap_drvdata` stores char-device state, byte leftovers, MMIO base, backend config, register map, open flag, and lock. `struct hwicap_driver_config` abstracts backend `get_configuration`, `set_configuration`, `get_status`, and `reset`. `struct config_registers` maps logical ICAP registers to family-specific numeric indexes. `hwicap_type_1_read()` and `hwicap_type_1_write()` build Type 1 packet headers. Constants cover Type 1/2 masks, commands such as `XHI_CMD_DESYNCH`, sync/dummy/noop packets, disabled CRC word, and status bits.

Control flow: no direct runtime flow except inline packet-header helpers used by `xilinx_hwicap.c`.

State and persistence: this header declares the shape of runtime state but does not allocate it. State persists per open device in `hwicap_drvdata`.

Dependencies and integration: included by common, FIFO, and buffer ICAP files. It is the contract between high-level char-device logic and transport-specific MMIO operations.

Risks: field layout and vtable signatures are shared across compilation units. Incorrect register maps or packet bit shifts can corrupt FPGA configuration. `UNIMPLEMENTED` family values are handled by callers only by choosing which registers to use; adding new families requires complete map review.

Test signals: compile all HWICAP objects, verify packet headers against Xilinx ICAP specs, read family-specific IDCODE/STAT registers, and run backend tests that exercise status masks and command constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/xilinx_hwicap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/Kconfig

Purpose: Kconfig menu for Xillybus PCIe/OF and XillyUSB FPGA interfaces.

Important APIs/types/functions: Defines `XILLYBUS_CLASS` as an internal tristate, `XILLYBUS` as the generic FPGA interface depending on PCI or OF, transport options `XILLYBUS_PCIE` and `XILLYBUS_OF`, and independent USB option `XILLYUSB`.

Control flow: no runtime flow; configuration selects which modules are built and which shared pieces are selected.

State and persistence: no runtime state. Build state is persisted in the kernel `.config`.

Dependencies and integration: `XILLYBUS` selects `CRC32` and `XILLYBUS_CLASS`; PCIe depends on `PCI_MSI`; OF depends on `OF`, `HAS_DMA`, and `HAS_IOMEM`; XillyUSB depends on `USB` and also selects `CRC32` and the class module.

Risks: `XILLYUSB` intentionally does not depend on `XILLYBUS`, so class/core assumptions must remain separated. Missing `XILLYBUS_CLASS` selection would break device-node lookup. PCIe requires MSI support; systems without MSI cannot use that transport.

Test signals: build matrix for built-in/module/disabled combinations of class, core, PCIe, OF, and USB; confirm dependencies prevent invalid configs and that module names match help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/Makefile

Purpose: Kbuild object mapping for Xillybus drivers.

Important APIs/types/functions: Maps `CONFIG_XILLYBUS_CLASS` to `xillybus_class.o`, `CONFIG_XILLYBUS` to `xillybus_core.o`, `CONFIG_XILLYBUS_PCIE` to `xillybus_pcie.o`, `CONFIG_XILLYBUS_OF` to `xillybus_of.o`, and `CONFIG_XILLYUSB` to `xillyusb.o`.

Control flow: no runtime flow.

State and persistence: no runtime state.

Dependencies and integration: implements the module split described by Kconfig: shared class, shared PCIe/OF core, transport wrappers, and independent USB driver.

Risks: transport modules depend on symbols exported by class/core according to Kconfig selections; Makefile/Kconfig drift can produce unresolved symbols.

Test signals: compile all Kconfig combinations, inspect module dependencies, and modprobe PCIe/OF/USB variants with `xillybus_class` available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus.h -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus.h

Purpose: Shared private header for PCIe/OF Xillybus transport wrappers and the Xillybus core.

Important APIs/types/functions: Defines `struct xilly_buffer` DMA buffer descriptors, `struct xilly_idt_handle` parsed IDT metadata, `struct xilly_channel` per-stream buffer/locking/state for FPGA-write and FPGA-read directions, `struct xilly_endpoint` common endpoint state, and `struct xilly_mapping` DMA unmap metadata. Declares `xillybus_isr()`, `xillybus_init_endpoint()`, `xillybus_endpoint_discovery()`, and `xillybus_endpoint_remove()`.

Control flow: no direct flow; the structures encode the core data path. Naming is FPGA-centric: `wr_*` buffers are written by the FPGA and read by host `read()`, while `rd_*` buffers are read by the FPGA and written by host `write()`.

State and persistence: declares runtime-only endpoint/channel state including DMA buffers, indices, EOF/hangup flags, waitqueues, mutexes/spinlocks, work items, message counters, and fatal error state.

Dependencies and integration: shared by `xillybus_core.c`, `xillybus_pcie.c`, and `xillybus_of.c`; depends on Linux device, DMA, interrupt, cdev, locking, and workqueue APIs.

Risks: this is a tight ABI across modules. The channel lock/index fields are interpreted by ISR, file operations, and workqueue code, so changes require full locking-order review. Direction naming can cause read/write confusion.

Test signals: compile PCIe and OF transports with the core, run endpoint discovery, open every generated node, and stress bidirectional DMA with read/write/poll/seek/close while interrupts arrive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.c -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.c

Purpose: Shared class and character-device registry for Xillybus and XillyUSB. It creates `/dev/xillybus_*` or enumerated `/dev/xillyusb_##_*` device nodes from IDT-provided stream names and maps inodes back to driver-private endpoint/channel indices.

Important APIs/types/functions: `struct xilly_unit` tracks one registered cdev range, private endpoint pointer, name prefix, major/minor span, and list node. `xillybus_init_chrdev()` allocates a char-dev region, cdev, and device nodes. `xillybus_cleanup_chrdev()` destroys nodes and unregisters the range. `xillybus_find_inode()` maps an inode major/minor to private data and stream index. Module init/exit registers the `xillybus` class.

Control flow: registration optionally enumerates a unique unit name, allocates `num_nodes` minors, adds one cdev covering the range, scans the NUL-separated IDT name list, creates class devices named `<unit>_<idt-name>`, validates that name data is neither short nor long, and records the unit. Cleanup finds the unit by private pointer, destroys every minor, deletes cdev, unregisters the range, removes the list entry, and frees state. Inode lookup scans the unit list under a mutex and returns the matching private pointer plus minor offset.

State and persistence: `unit_list` and `unit_mutex` are module-global runtime state. Device nodes exist while endpoints are registered but are removed on endpoint cleanup or module unload.

Dependencies and integration: used by PCIe/OF Xillybus core and XillyUSB. It depends on class devices, cdev, dynamic major allocation, and IDT name strings from hardware discovery.

Risks: IDT name-list length must exactly match `num_nodes`; otherwise registration unrolls. Device names are built into a 48-byte stack buffer and unit names into 16 bytes, so truncation/uniqueness behavior matters. `xillybus_find_inode()` relies on the unit list remaining stable until callers take their own references; XillyUSB adds `kref_mutex` around that gap.

Test signals: register/remove units with multiple nodes, long/short/malformed name lists, duplicate prefixes with enumeration, open devices before and during disconnect, and verify no stale majors/minors or class devices remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.h -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.h

Purpose: Header exposing the Xillybus class registry to core and USB drivers.

Important APIs/types/functions: Declares `xillybus_init_chrdev()`, `xillybus_cleanup_chrdev()`, and `xillybus_find_inode()`.

Control flow: no runtime flow; it defines the interface for creating/removing named device nodes and resolving an opened inode.

State and persistence: no state in the header. Runtime state lives in `xillybus_class.c`.

Dependencies and integration: included by `xillybus_core.c` and `xillyusb.c`; depends on Linux device, file-operations, inode, and module types.

Risks: prototype changes affect both PCIe/OF and USB variants. The `private_data` pointer is opaque, so caller lifetime rules are external to this header.

Test signals: compile both families and verify device-node creation/open paths use the declared API correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_core.c -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_core.c

Purpose: Transport-independent core for PCIe and OF Xillybus FPGA interfaces. It discovers FPGA stream definitions, allocates DMA buffers, handles interrupt messages, creates character devices, and implements read/write/flush/seek/poll semantics over FPGA FIFOs.

Important APIs/types/functions: `xillybus_isr()` processes FPGA messages (`RELEASEBUF`, `QUIESCEACK`, `FIFOEOF`, `FATAL_ERROR`, `NONEMPTY`). `xilly_map_single()` and `xilly_get_dma_buffers()` allocate/map DMA buffers and program FPGA buffer-address registers. `xilly_setupchannels()` builds channels from the IDT. `xilly_obtain_idt()` and `xilly_scan_idt()` fetch and parse stream names/descriptors. File operations are `xillybus_read()`, `xillybus_write()`, `xillybus_flush()`, `xillybus_open()`, `xillybus_release()`, `xillybus_llseek()`, and `xillybus_poll()`. Endpoint lifecycle exports are `xillybus_init_endpoint()`, `xillybus_endpoint_discovery()`, and `xillybus_endpoint_remove()`.

Control flow: endpoint discovery writes host endianness, bootstraps a temporary message buffer, clears message state, negotiates DMA width/quiesce/IDT length, enables DMA, fetches the IDT, validates and parses names/channel descriptors, allocates final DMA buffers, programs buffer addresses, and registers char devices. IRQ handling synchronizes the message DMA buffer, validates message counters, updates per-channel buffer indices/end offsets/EOF/nonempty flags under spinlocks, wakes waiters, queues autoflush for async write channels, and acknowledges messages. `read()` drains FPGA-written buffers to userspace, returns buffers to hardware, optionally sends offset-limit/flush requests, honors sync/partial/nonblocking rules, and detects EOF. `write()` fills host-written buffers from userspace, submits buffers with end offsets, queues delayed autoflush for async channels, and flushes synchronously when required. Release closes directions and waits for read-side EOF acknowledgement.

State and persistence: endpoint/channel state is runtime-only: DMA buffers, buffer indices, read/write reference counts, EOF/hangup/ready/full flags, workqueue, IDT-derived attributes, message counter, and fatal-error flag. Device nodes persist only for the endpoint lifetime. No filesystem data is stored.

Dependencies and integration: used by `xillybus_pcie.c` and `xillybus_of.c` after they map registers, configure DMA masks, and request interrupts. Integrates with `xillybus_class`, Linux DMA mapping, MMIO, workqueues, waitqueues, poll, CRC32, and char-device APIs.

Risks: concurrency is the main risk: the file documents a strict lock order across write/read mutexes, endpoint register mutex, and direction spinlocks. DMA sync direction must match FPGA ownership or data corruption follows. IDT parsing and CRC/length checks protect against malformed hardware descriptions. Fatal message sync loss stops operation. Nonblocking read support is intentionally limited to async/nonempty-capable channels. Close waits can leave hardware in a messy state if EOF acknowledgement never arrives.

Test signals: discover a real Xillybus FPGA over PCIe/OF, validate IDT CRC/name parsing, create all nodes, stress read/write with synchronous and asynchronous channels, partial and non-partial modes, nonblocking open/read/write restrictions, poll, llseek on seekable channels, flush/autoflush timeouts, interrupt message counter errors, fatal-error propagation, endpoint removal with open files, and DMA mask variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_of.c -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_of.c

Purpose: Open Firmware / Device Tree transport wrapper for the shared Xillybus core.

Important APIs/types/functions: Device matches `xillybus,xillybus-1.00.a` and deprecated `xlnx,xillybus-1.00.a`. `xilly_drv_probe()` initializes an endpoint, maps the platform MMIO resource, requests the platform IRQ using `xillybus_isr()`, and calls `xillybus_endpoint_discovery()`. `xilly_drv_remove()` calls `xillybus_endpoint_remove()`.

Control flow: probe allocates devres-managed endpoint state, stores it as driver data, sets module owner, ioremaps resource 0, obtains IRQ 0, requests the IRQ, and delegates all discovery/device-node setup to the core. Remove delegates cleanup/quiesce to the core.

State and persistence: only runtime endpoint state stored on the platform device; devres owns MMIO/IRQ lifetime.

Dependencies and integration: depends on OF matching, platform devices, devm MMIO/IRQ helpers, and the shared Xillybus core/class modules.

Risks: probe returns directly on MMIO mapping failure after endpoint allocation, relying on devres cleanup. `platform_get_irq()` result is not explicitly checked before `devm_request_irq()`, so negative IRQ handling depends on request helper behavior. Device Tree resource correctness is mandatory.

Test signals: boot with matching DT node, verify MMIO/IRQ resources, successful endpoint discovery and device nodes, interrupt-driven I/O, remove/unbind cleanup, and deprecated compatible support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_pcie.c -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_pcie.c

Purpose: PCIe transport wrapper for the shared Xillybus core.

Important APIs/types/functions: Matches Xillybus PCI device ID `0xebeb` for Xilinx, Altera, Actel, and Lattice vendor IDs. `xilly_probe()` initializes endpoint state, enables the PCI device, maps BAR0, enables bus mastering and MSI, requests `xillybus_isr()`, selects a DMA mask, and calls `xillybus_endpoint_discovery()`. `xilly_remove()` calls `xillybus_endpoint_remove()`.

Control flow: probe allocates a core endpoint, stores it in PCI drvdata, uses pcim-managed enable/map resources, disables L0s due to packet drop history, validates BAR0 as memory, maps BAR0, enables MSI, requests the interrupt, prefers a 32-bit DMA mask unless only 64-bit works, records DAC use, and delegates discovery. Remove delegates endpoint cleanup.

State and persistence: runtime endpoint state is stored in PCI drvdata and devres/pcim-managed resources. No persistent state.

Dependencies and integration: depends on PCI, MSI, BAR0 MMIO, DMA mask APIs, and the shared Xillybus core/class modules.

Risks: MSI enablement is mandatory and the driver does not include an INTx fallback. The 32-bit-first DMA mask choice works around old hardware but may limit DMA addressing. L0s is forcibly disabled for reliability. Endpoint cleanup must quiesce DMA before PCI-managed resources disappear.

Test signals: probe supported vendor/device IDs, verify BAR0 mapping and MSI interrupt delivery, DMA mask fallback on 32-bit/64-bit platforms, stream discovery and I/O, link power-management behavior, remove/unbind with active channels, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillyusb.c -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillyusb.c

Purpose: USB transport implementation for Xillybus FPGA IP cores. It discovers channel definitions over a control opcode protocol, creates character devices via the shared Xillybus class, and moves upstream/downstream stream data through USB bulk endpoints and software FIFOs.

Important APIs/types/functions: `struct xillyfifo` is a ring FIFO made from page buffers. `struct xillyusb_endpoint` owns one USB bulk endpoint, free/filled buffer lists, URB anchor, FIFO, work item, drain/shutdown flags, and endpoint number. `struct xillyusb_channel` owns per-stream readable/writable attributes, open state, FIFOs/endpoints, mutexes, checkpoint counters, flush state, and seekability. `struct xillyusb_dev` owns USB device refs, workqueues, global error state, base message/input endpoints, channel array, and stream parsing leftovers. Key functions include `fifo_init/read/write`, endpoint allocation/quiesce/dealloc, URB completers, `try_queue_bulk_in/out()`, `process_bulk_in()`, `xillyusb_send_opcode()`, `flush_downstream()`, `xillyusb_open/read/write/flush/release/llseek/poll()`, discovery/probe/disconnect, and module init/exit.

Control flow: module init creates a wakeup workqueue and registers a soft-unbind USB driver for Xilinx/Altera product `0xebbe`. Probe allocates device state, base message OUT and shared IN endpoints, starts bulk IN URBs, sends quiesce, creates a temporary channel/FIFO, requests the IDT, waits for EOF, validates CRC/version/length, sets up final channel descriptors and endpoint requirements, then registers class devices with enumerated names. Reads drain the channel input FIFO, update consumed-byte checkpoints, send checkpoint/push opcodes to control FPGA flow, wait for data/EOF, and support limited nonblocking behavior. Writes fill the channel output FIFO, queue bulk OUT URBs, update byte counts, and optionally flush synchronously by checkpointing FPGA receipt. Release sends close opcodes, waits for read EOF, quiesces/deallocates per-open output endpoints, and drops the device kref. Disconnect removes char devices, tries to send global quiesce, reports a global error, quiesces active endpoints/URBs, clears interface data, and releases the final ref.

State and persistence: all state is runtime USB session state: krefs, per-channel open flags, FIFO contents, endpoint buffers, outstanding URBs, checkpoint counters, in-stream leftover parsing, global error code, and class devices. No data persists beyond device lifetime.

Dependencies and integration: depends on USB core bulk pipes, URBs/anchors, workqueues, CRC32, waitqueues, kref lifetime management, the shared `xillybus_class` API, and the XillyUSB opcode/IDT protocol implemented by FPGA logic.

Risks: lifetime is delicate because device disconnect can race open/read/write/release; `kref_mutex`, `report_io_error()`, and `wakeup_all()` coordinate cleanup. Bulk IN parsing must preserve partial data messages across URBs (`in_bytes_left`/`leftover_chan_num`) and validate opcode counters. FIFO fill accounting relies on spinlock barriers. Flush/checkpoint cancellation handles races with timed-out previous flushes. Soft unbind requires explicit URB quiesce. Downstream channels above index 13 are silently ignored because USB endpoint numbers would exceed 15.

Test signals: plug supported XillyUSB devices, validate IDT CRC/version/name parsing, create enumerated class nodes, exercise readable/writable/synchronous/seekable channels, blocking and nonblocking read/write/poll, flush and checkpoint timeout/cancel paths, llseek address changes, high-throughput bulk URB recycling, malformed opcode/counter handling, unplug during active I/O, module unload with open files, and memory-leak/URB-anchor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillyusb.c -->
