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
