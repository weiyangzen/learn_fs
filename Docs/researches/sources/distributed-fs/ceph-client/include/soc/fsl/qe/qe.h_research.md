# sources/distributed-fs/ceph-client/include/soc/fsl/qe/qe.h

Purpose: exposes QUICC Engine common services, MURAM allocation, parallel I/O, pin muxing, command issuance, clock/BRG management, firmware format, buffer descriptors, and QE register bit definitions.

Important APIs and types: `enum qe_clock`, `qe_clock_is_brg()`, `qe_reset()`, MURAM alloc/free/address/DMA helpers and QE aliases, `struct qe_pio_regs`, parallel I/O APIs, QE GPIO pin APIs, `qe_issue_cmd()`, BRG/SNUM/RISC discovery APIs, `qe_alive_during_sleep()`, register set/clear macros, `struct qe_firmware` and `struct qe_firmware_info`, `qe_upload_firmware()`, `qe_get_firmware_info()`, `qe_usb_clock_set()`, and `struct qe_bd`. Numerous macros define alignment, RISC allocation, filtering table descriptors, communication direction, CMX routing, CECR commands/subblocks/protocols, BRG, timers, SDMA, CP, IRAM, UPC, GUEMR, UCC mode, event, and bus/function-code bits.

Control flow: platform code initializes MURAM/QE, configures pins/clocks/BRGs, uploads firmware if needed, allocates parameter RAM/BDs, and protocol drivers issue QE commands and manipulate UCC/MURAM resources.

State and persistence: runtime state includes QE registers, MURAM allocator state, SNUM allocation, firmware/microcode state, PIO mux state, and buffer descriptors. No filesystem persistence is handled here.

Dependencies and integration points: includes CPM and QE memory-map headers, OF/address helpers, genalloc, spinlocks, and device APIs. It is the central integration point for QE users.

Risks and test signals: risks include disabled-config stubs returning `-ENOSYS`, MURAM lifetime leaks, pinmux conflicts, command subblock/protocol mistakes, endian MMIO misuse, firmware format incompatibility, and sleep behavior differences on PPC85xx. Test QE probe/reset, MURAM alloc/free/fixed/devm paths, BRG rate setting, SNUM exhaustion, firmware upload/CRC consumers, pinmux from device tree, and UCC protocol bring-up.
