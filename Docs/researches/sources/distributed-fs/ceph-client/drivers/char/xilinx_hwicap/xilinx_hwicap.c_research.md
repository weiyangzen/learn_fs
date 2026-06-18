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
