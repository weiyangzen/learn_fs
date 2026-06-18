# Research: subset-b-004047

This grouped report covers the requested CEC platform drivers, CEC USB drivers, and B2C2 media-common support files. Each section is bounded with the exact reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/ao-cec-g12a.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/ao-cec-g12a.c

## Purpose
This is the Amlogic Meson AO-CECB CEC controller driver for G12A/SM1 generation SoCs. It exposes a Linux CEC adapter backed by a memory-mapped AO CEC block, integrates with an HDMI CEC notifier for connector information, and registers an internal dual-divider clock that derives the 32.768 kHz CEC core clock from the oscillator.

## Important APIs, Types, and Functions
The main state type is `struct meson_ao_cec_g12a_device`, holding the platform device, top-level regmap, indirect CEC regmap, CEC adapter, notifier, clock handles, RX message buffer, and SoC-specific data. `struct meson_ao_cec_g12a_data` gates the SM1-only `CECB_CTRL2` setup. The internal clock is represented by `struct meson_ao_cec_g12a_dualdiv_clk` and `clk_ops` for recalc/enable/disable/is_enabled. CEC framework callbacks are `meson_ao_cec_g12a_adap_enable`, `meson_ao_cec_g12a_set_log_addr`, and `meson_ao_cec_g12a_transmit`.

## Control Flow
Probe parses the HDMI phandle, allocates a CEC adapter, maps MMIO, creates two regmaps, requests a threaded IRQ, obtains `oscin`, registers/enables the dual-divider clock, optionally resets the device, registers the notifier, and registers the adapter. Enable resets the controller, configures glitch filtering and system/gated clocks, optionally programs `CECB_CTRL2`, and unmasks interrupts. Transmit checks RX lock and TX busy state, writes TX bytes/count, and starts the controller with the correct signal-free-time type. The hard IRQ only wakes the thread if interrupt status is nonzero; the thread clears status and reports TX done/NACK/arbitration/error or dispatches RX data.

## State and Persistence
Driver state is in `meson_ao_cec_g12a_device`. Hardware logical address bits are stored in `CECB_LADD_LOW/HIGH`, always adding unregistered/broadcast address 15. RX state is transient in `rx_msg`; TX completion is reported directly from interrupt status. There is no persistent configuration beyond DT-compatible match data and clock/reset resources.

## Dependencies and Integration Points
The driver depends on platform device resources, regmap, clock provider APIs, optional reset control, `media/cec.h`, and `cec-notifier`. DT compatibles are `amlogic,meson-g12a-ao-cec` and `amlogic,meson-sm1-ao-cec`. The indirect CEC register bus is wrapped as an 8-bit regmap using custom read/write callbacks through `CECB_RW_REG`.

## Risks and Test Signals
Important risks are timing correctness in the dual-divider setup, indirect-register polling timeouts, RX lock handling before TX, and correct interrupt status translation. `meson_ao_cec_g12a_dualdiv_clk_recalc_rate` reads `CECB_CLK_CNTL_REG0` twice where the second read appears intended for REG1, and the M2 extraction uses `CECB_CLK_CNTL_M1`; tests should inspect reported clock rate. Hardware tests should cover logical address add/remove, poll messages, directed and broadcast transmit, NACK/arbitration loss, RX length clamping, and SM1-specific `CTRL2` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/ao-cec-g12a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/ao-cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/ao-cec.c

## Purpose
This is the older Amlogic Meson GX AO CEC controller driver. It exposes a single-logical-address CEC adapter over the CEC framework using raw MMIO and an indirect CEC register access window.

## Important APIs, Types, and Functions
`struct meson_ao_cec_device` stores the platform device, mapped base, core clock, spinlock for indirect register access, notifier, adapter, and RX message. Low-level helpers `meson_ao_cec_read`, `meson_ao_cec_write`, and `meson_ao_cec_wait_busy` serialize CEC register access through `CEC_RW_REG`. CEC callbacks are `meson_ao_cec_adap_enable`, `meson_ao_cec_set_log_addr`, and `meson_ao_cec_transmit`.

## Control Flow
Probe obtains the HDMI device from DT, allocates the adapter, maps MMIO, requests a threaded IRQ, gets/enables the `core` clock, sets it to 32768 Hz, resets the device, registers the notifier, and registers the adapter. Enable masks interrupts, asserts reset, enables the gated clock, releases reset, clears RX/TX buffers, programs arbitration timings, and unmasks TX/RX interrupts. Transmit aborts a busy TX, writes message bytes and length, and requests current-message transmission. The IRQ thread handles TX status first, then runs RX processing every interrupt pass.

## State and Persistence
State is volatile: the CEC hardware stores message FIFOs, logical address 0, timing registers, and interrupt status. The driver stores only one in-flight RX message and no persistent logical address configuration. Logical address invalid disables address 0 and clears hardware buffers.

## Dependencies and Integration Points
The driver integrates with `cec_notifier_parse_hdmi_phandle`, `cec_notifier_cec_adap_register`, the CEC core, platform MMIO resources, IRQs, reset, and a `core` clock. DT compatible is `amlogic,meson-gx-ao-cec`.

## Risks and Test Signals
The indirect register access window is protected by a spinlock and 5 ms busy wait; timeout paths are critical. RX processing assumes `CEC_RX_NUM_MSG == 1` and clears/acks buffers after each interrupt. Test with clock-rate setup, reset recovery, busy TX abort, RX/TX interrupt clearing, logical address invalidation, and all signal-free-time modes. Probe failure tests should verify adapter/notifier/clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/ao-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/Makefile

## Purpose
This Makefile builds the Samsung S5P/Exynos HDMI CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_SAMSUNG_S5P` to the composite object `s5p-cec.o`, with `s5p-cec-y` made from `s5p_cec.o` and `exynos_hdmi_cecctrl.o`.

## Control Flow
Kbuild compiles the framework-facing driver and low-level register-control helper into one module or built-in object depending on the Kconfig setting.

## State and Persistence
No runtime state is present. The file defines build composition only.

## Dependencies and Integration Points
It depends on the surrounding Kconfig selecting `CONFIG_CEC_SAMSUNG_S5P`. The split confirms that `s5p_cec.c` can call helper functions implemented in `exynos_hdmi_cecctrl.c`.

## Risks and Test Signals
Build tests should verify both objects are linked and exported helper prototypes match. A missing helper object would produce unresolved symbols for reset, divider, interrupt-mask, TX, RX, and status routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/exynos_hdmi_cec.h -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/exynos_hdmi_cec.h

## Purpose
This header declares the low-level Samsung Exynos HDMI CEC helper API used by the S5P CEC framework driver.

## Important APIs, Types, and Functions
It includes `s5p_cec.h` and declares helpers for divider setup, RX enable, TX/RX interrupt masking, full/TX/RX reset, RX filter threshold setup, TX packet copy/start, logical address programming, status reading, pending interrupt clearing, and RX buffer extraction.

## Control Flow
The header provides the call contract from `s5p_cec.c` into `exynos_hdmi_cecctrl.c`. Adapter enable calls reset, divider, threshold, unmask, and RX enable helpers; transmit calls `s5p_cec_copy_packet`; IRQ paths call status, clear-pending, reset, and RX buffer helpers.

## State and Persistence
It does not define storage. All state is passed through `struct s5p_cec_dev *cec`, which carries MMIO base, PMU regmap, CEC adapter, and TX/RX state.

## Dependencies and Integration Points
The header depends on Linux regmap through the implementation and on local `s5p_cec.h`/`regs-cec.h` definitions. It is a private in-directory interface, not a global kernel API.

## Risks and Test Signals
The include cycle with `s5p_cec.h` is unusual but works through include guards. Prototype changes must be kept synchronized with `exynos_hdmi_cecctrl.c`; compile testing is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/exynos_hdmi_cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/exynos_hdmi_cecctrl.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/exynos_hdmi_cecctrl.c

## Purpose
This file implements low-level register access for the Samsung S5P/Exynos HDMI CEC hardware. It handles clock divider programming, reset, interrupt masking, transmit buffer setup, logical address programming, status aggregation, and RX buffer reads.

## Important APIs, Types, and Functions
The public helper functions are declared in `exynos_hdmi_cec.h`. `s5p_cec_set_divider` programs the HDMI PHY PMU divider through `cec->pmu` and local CEC divisor registers. `s5p_cec_copy_packet` writes TX bytes at 4-byte-spaced registers, sets byte count, retry count, start bit, and broadcast mode. `s5p_cec_get_status` folds multiple 8-bit status registers into a 32-bit driver status word.

## Control Flow
Adapter enable calls divider setup, threshold setup, interrupt unmasking, and RX enable. Transmit writes the packet and starts hardware. IRQ handling reads status through `s5p_cec_get_status`, clears TX/RX pending bits with `s5p_clr_pending_tx/rx`, and for successful RX reads bytes using `s5p_cec_get_rx_buf`.

## State and Persistence
State lives in hardware registers. The PMU register `EXYNOS_HDMI_PHY_CONTROL` stores divider bits; CEC registers hold logical address, filter threshold, TX/RX control, IRQ masks, status, and buffers. No persistent storage is written.

## Dependencies and Integration Points
The implementation depends on local register offsets in `regs-cec.h`, `struct s5p_cec_dev` in `s5p_cec.h`, `regmap` for PMU syscon access, and byte MMIO accessors.

## Risks and Test Signals
`s5p_cec_get_rx_buf` uses a fixed 40-byte debug buffer and `sprintf` while reading up to 16 bytes, which is tight but fits the formatted data. The divider code uses floating literal arithmetic (`CEC_DIV_RATIO * 0.00005`) in C, yielding a small divisor value; clock validation is important. Test reset, RX filter threshold, broadcast vs directed TX, retry encoding, status-bit mapping, and PMU access failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/exynos_hdmi_cecctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/regs-cec.h -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/regs-cec.h

## Purpose
This private header defines Samsung S5P CEC register offsets, interrupt bits, TX/RX control bits, logical address mask, and the PMU HDMI PHY control offset.

## Important APIs, Types, and Functions
There are no functions. Important definitions include `S5P_CEC_STATUS_0..3`, `S5P_CEC_IRQ_MASK/CLEAR`, TX and RX buffer base offsets, `S5P_CEC_TX_CTRL_START/BCAST/RESET`, `S5P_CEC_RX_CTRL_ENABLE/RESET`, and `EXYNOS_HDMI_PHY_CONTROL`.

## Control Flow
`exynos_hdmi_cecctrl.c` uses these constants to program the hardware in reset, enable, transmit, receive, and IRQ-clear flows. Buffer offsets are spaced by four bytes and are used by loops that add `i * 4`.

## State and Persistence
The file documents hardware state layout only. Runtime values are held in MMIO registers.

## Dependencies and Integration Points
It is consumed by the Samsung S5P CEC driver files and must match the SoC register map. No external subsystem directly includes it.

## Risks and Test Signals
Wrong offsets or bit values would cause silent hardware misbehavior. Tests require hardware or register-level emulation checking TX start, RX enable, interrupt mask/clear, buffer byte placement, and logical address programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/regs-cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/s5p_cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/s5p_cec.c

## Purpose
This is the framework-facing Samsung S5P HDMI CEC platform driver. It allocates/registers the CEC adapter, handles runtime PM, maps IRQs to CEC core notifications, and delegates register operations to `exynos_hdmi_cecctrl.c`.

## Important APIs, Types, and Functions
CEC callbacks are `s5p_cec_adap_enable`, `s5p_cec_adap_log_addr`, and `s5p_cec_adap_transmit`. IRQ work is split between `s5p_cec_irq_handler` and `s5p_cec_irq_handler_thread`. Probe/remove and runtime PM are implemented with `s5p_cec_probe`, `s5p_cec_remove`, `s5p_cec_runtime_suspend`, and `s5p_cec_runtime_resume`.

## Control Flow
Probe parses the HDMI phandle, allocates state, requests IRQ, obtains the `hdmicec` clock, gets the PMU syscon, maps registers, allocates a CEC adapter, registers a notifier, registers the adapter, and enables runtime PM. Enabling resumes the device, resets hardware, programs divider/filter, unmasks interrupts, and enables RX. Disabling masks interrupts and drops runtime PM. Hard IRQ snapshots status and sets `cec->tx`/`cec->rx`; the thread calls `cec_transmit_done` or `cec_received_msg`.

## State and Persistence
`struct s5p_cec_dev` stores TX/RX state enum values, one RX `cec_msg`, clock, PMU regmap, notifier, IRQ, and mapped registers. Runtime PM controls clock lifetime. No durable configuration is stored.

## Dependencies and Integration Points
The driver integrates with platform resources, OF compatible `samsung,s5p-cec`, CEC notifier connector data, `pm_runtime`, `syscon_regmap_lookup_by_phandle`, and local register helpers. The optional `needs-hpd` DT property adds `CEC_CAP_NEEDS_HPD`.

## Risks and Test Signals
RX overrun is only logged if the worker has not consumed the previous message. TX retry count is forced to at least one. Test runtime suspend/resume, HPD-required capability, TX done/NACK/error mapping, RX error reset, message length clamping, and cleanup paths when notifier or adapter registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/s5p_cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/s5p_cec.h -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/s5p_cec.h

## Purpose
This header defines the Samsung S5P CEC driver state, status-bit meanings, buffer sizing, and TX/RX state enum.

## Important APIs, Types, and Functions
Key definitions are `CEC_STATUS_TX_*`, `CEC_STATUS_RX_*`, `CEC_RX_BUFF_SIZE`, `CEC_TX_BUFF_SIZE`, `enum cec_state`, and `struct s5p_cec_dev`. The state structure contains the CEC adapter, clock, device, mutex, PMU regmap, notifier, IRQ, MMIO base, RX/TX state, and current RX message.

## Control Flow
The status bits are produced by `s5p_cec_get_status` and consumed by `s5p_cec_irq_handler`. The state enum gates threaded IRQ reporting through `cec_transmit_done` and `cec_received_msg`.

## State and Persistence
This file defines volatile driver state only. `rx`, `tx`, and `msg` are transient interrupt-processing state; hardware and runtime PM own actual device state.

## Dependencies and Integration Points
The header includes Linux platform, clock, interrupt, runtime PM, media CEC, and the local low-level headers. It is private to the S5P driver build.

## Risks and Test Signals
The header includes itself indirectly through `exynos_hdmi_cec.h`, relying on guards. Status-bit definitions must match how `exynos_hdmi_cecctrl.c` packs hardware registers. Compile tests and IRQ status mapping tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/s5p_cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/Makefile

## Purpose
This Makefile builds the SECO x86 CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_SECO` to `seco-cec.o`.

## Control Flow
Kbuild includes the SECO driver when the config option is enabled as a module or built-in.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The file depends on the surrounding Kconfig to select the driver. The implementation handles ACPI, GPIO IRQ, SMBus I/O ports, CEC, and optional RC input.

## Risks and Test Signals
Build coverage should confirm the object is linked only when `CONFIG_CEC_SECO` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/seco-cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/seco-cec.c

## Purpose
This driver supports SECO x86 boards with an embedded microcontroller that exposes HDMI CEC and optionally RC5 IR over a Braswell SMBus I/O-port interface.

## Important APIs, Types, and Functions
`struct secocec_data` stores device, platform device, CEC adapter, notifier, optional RC device, input phys string, and IRQ. `smb_word_op` performs low-level SMBus word transactions through fixed I/O ports. CEC callbacks are `secocec_adap_enable`, `secocec_adap_log_addr`, and `secocec_adap_transmit`. Interrupt handlers call `secocec_rx_done`, `secocec_tx_done`, and optional `secocec_ir_rx`.

## Control Flow
Probe finds the related HDMI PCI device using DMI, requests the SMBus I/O region, validates ACPI/GPIO IRQ, checks firmware version, requests a threaded IRQ, allocates/registers the CEC adapter and notifier, and optionally registers RC input. Enabling clears status and enables CEC interrupts. Transmit writes payload length, opcode, data words, and header byte to fire the message. IRQ reads high-level status, then CEC status, dispatches RX/TX completions, handles IR, and clears status bits.

## State and Persistence
The microcontroller stores logical address, pending TX/RX data, CEC status, enable bits, firmware version, and IR data. Driver state is volatile. No persistent configuration is written, though firmware version must be at least `SECOCEC_LATEST_FW`.

## Dependencies and Integration Points
The driver depends on ACPI ID `CEC00001`, DMI match for UDOO x86, PCI device lookup for connector binding, GPIO-to-IRQ, I/O-port SMBus access, CEC notifier, and optional `CONFIG_CEC_SECO_RC` RC-core support.

## Risks and Test Signals
Fixed SMBus I/O ports and request/release discipline are high risk. Payload packing uses pairs of data bytes and assumes valid CEC length. In `secocec_rx_done`, odd payload lengths can index `payload_msg[i + 1]` beyond the logical payload. Test firmware rejection, SMBus timeout/error handling, IRQ clearing, RX overflow/error, TX NACK/error, suspend/resume interrupt enable state, and optional IR decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/seco-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/seco-cec.h -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/seco-cec.h

## Purpose
This header defines SECO CEC microcontroller registers, SMBus I/O-port constants, status bits, enable bits, firmware requirement, and IR bit layout.

## Important APIs, Types, and Functions
There are no functions. Key constants include `SECOCEC_MICRO_ADDRESS`, `SECOCEC_VERSION`, `SECOCEC_ENABLE_REG_1`, `SECOCEC_STATUS`, read/write CEC data register ranges, `SECOCEC_IR_READ_DATA`, and masks for CEC RX/TX status and IR RC5 fields.

## Control Flow
`seco-cec.c` uses these constants for SMBus word reads/writes in adapter enable, logical address setting, transmit, receive, IRQ, IR, suspend, resume, and probe firmware validation.

## State and Persistence
The header maps microcontroller state and Braswell host status/control registers. Runtime persistence is in the external controller, not the Linux driver.

## Dependencies and Integration Points
The I/O-port constants target the Braswell SMBus host controller. The register map represents the STM32-based SECO microcontroller protocol used by the platform driver.

## Risks and Test Signals
`SECOCEC_STATUS_REG_1_IR_PASSTHR` references a misspelled/undefined macro-like name and should be compile-checked if used. Hardware tests should confirm register definitions against firmware documentation, especially status clearing masks and data word ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/seco-cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/sti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/sti/Makefile

## Purpose
This Makefile builds the STiH4xx CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_STI` to `stih-cec.o`.

## Control Flow
Kbuild compiles the STi CEC driver as selected by Kconfig.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The implementation depends on platform MMIO, a CEC clock, IRQ, and CEC notifier.

## Risks and Test Signals
Build testing with `CONFIG_CEC_STI=m/y` verifies the object path and module composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/sti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/sti/stih-cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/sti/stih-cec.c

## Purpose
This is the STMicroelectronics STiH4xx CEC platform driver. It registers a CEC adapter over a memory-mapped transceiver with separate TX/RX byte arrays and status registers.

## Important APIs, Types, and Functions
`struct stih_cec` stores adapter, device, clock, MMIO base, IRQ status, and notifier. CEC callbacks are `stih_cec_adap_enable`, `stih_cec_adap_log_addr`, and `stih_cec_adap_transmit`. Completion helpers `stih_tx_done` and `stih_rx_done` translate hardware status to CEC core calls.

## Control Flow
Probe parses the HDMI phandle, maps registers, requests a threaded IRQ, gets `cec-clk`, allocates/registers notifier and adapter, and stores drvdata. Enable programs clock divider and timing thresholds, enables TX/RX arrays, configures control bits, clears address/status, and enables interrupts. Transmit writes message bytes to TX array and starts auto-SOM/EOM transmission. Hard IRQ snapshots/clears status; thread reports TX completion or received message.

## State and Persistence
Hardware holds logical address table, timing configuration, TX/RX byte arrays, and status. Driver stores only a last IRQ status snapshot and adapter/notifier resources. No persistent storage exists.

## Dependencies and Integration Points
DT compatible is `st,stih-cec`. The driver uses platform resources, clock API, threaded IRQs, CEC core, and notifier connector metadata.

## Risks and Test Signals
The driver does not call `clk_prepare_enable`; it reads rate only, so platform clock enable assumptions should be validated. Logical address invalid clears all addresses, otherwise addresses are ORed. Test TX ACK/NACK/error/arbitration status, RX min/max error suppression, zero-length RX, multi-logical-address programming, and interrupt status clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/sti/stih-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/stm32/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/stm32/Makefile

## Purpose
This Makefile builds the STM32 CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_STM32` to `stm32-cec.o`.

## Control Flow
Kbuild includes the STM32 CEC object when configured.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The object depends on the implementation using platform MMIO, regmap, CEC core, clocks, and optional reset resources.

## Risks and Test Signals
Build tests should verify the module is included for `CONFIG_CEC_STM32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/stm32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/stm32/stm32-cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/stm32/stm32-cec.c

## Purpose
This is the STMicroelectronics STM32 CEC controller driver. It registers a CEC adapter over a small regmap-backed MMIO block and streams TX/RX bytes through data registers under interrupt control.

## Important APIs, Types, and Functions
`struct stm32_cec` stores adapter, device, CEC and HDMI-CEC clocks, reset pointer, regmap, IRQ status, RX/TX messages, and TX byte index. Important functions are `cec_hw_init`, `stm32_tx_done`, `stm32_rx_done`, `stm32_cec_adap_enable`, `stm32_cec_adap_log_addr`, and `stm32_cec_adap_transmit`.

## Control Flow
Probe maps MMIO through `devm_regmap_init_mmio_clk`, requests a threaded IRQ, prepares the `cec` and optional `hdmi-cec` clocks, allocates/registers a CEC adapter with physical-address capability, initializes hardware, and stores drvdata. Enable turns on clocks and `CECEN`; disable turns them off. Transmit copies the message, sets `TXEOM` for one-byte messages, starts TX with `TXSOM`, and writes the header. IRQ snapshots/clears status; the thread writes additional bytes on `TXBR`, reports completion/error, collects RX bytes on `RXBR`, and reports on `RXEND`.

## State and Persistence
Driver state includes current TX message/count and current RX message. Logical addresses live in `CEC_CFGR.OAR`, and the controller is temporarily disabled while the address field is updated. No persistent storage is used.

## Dependencies and Integration Points
DT compatible is `st,stm32-cec`. The driver depends on regmap, clock framework, platform IRQ/MMIO, and CEC core. It currently does not use a notifier and therefore keeps `CEC_CAP_PHYS_ADDR` for userspace physical address control.

## Risks and Test Signals
`stm32_cec_adap_log_addr` ignores the return value of `regmap_read_poll_timeout`, so timeout behavior deserves review. RX length is incremented without an explicit `CEC_MAX_MSG_SIZE` guard. Test one-byte TX, multi-byte TXBR sequencing, TX error/NACK/arbitration mapping, RX overflow reset, logical address update during busy TX, optional clock absence, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/stm32/stm32-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/Makefile

## Purpose
This Makefile builds the NVIDIA Tegra CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_TEGRA` to `tegra_cec.o`.

## Control Flow
Kbuild compiles the Tegra implementation when the config option is enabled.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The implementation depends on platform MMIO, Tegra CEC clocking, IRQs, and CEC notifier integration.

## Risks and Test Signals
Build tests with `CONFIG_CEC_TEGRA` verify object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/tegra_cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/tegra_cec.c

## Purpose
This is the NVIDIA Tegra HDMI CEC driver for Tegra114/124/210. It registers a CEC adapter using a memory-mapped hardware engine with interrupt-driven TX FIFO feeding and RX byte collection.

## Important APIs, Types, and Functions
`struct tegra_cec` holds adapter, device, clock, MMIO base, notifier, IRQ, TX/RX completion flags, status, RX byte buffer/count, and TX register words/counts. CEC callbacks are `tegra_cec_adap_enable`, `tegra_cec_adap_log_addr`, `tegra_cec_adap_monitor_all_enable`, and `tegra_cec_adap_transmit`. `tegra_cec_error_recovery` resets hardware control and clears interrupts.

## Control Flow
Probe parses HDMI phandle, requests/remaps memory, gets/enables the `cec` clock, requests threaded IRQ, allocates/registers notifier and adapter, and supports monitor-all capability. Enable clears control/masks/status, programs filter and RX/TX timing constants, enables relevant interrupts, and sets TX/RX mode. Transmit builds per-byte TX register words with start/EOM/broadcast/retry bits and enables TX-register-empty interrupts. The hard IRQ handles underrun, arbitration, bus anomaly, frame transmitted/NACK, FIFO empty, and RX start/full; the thread reports CEC core completions.

## State and Persistence
TX/RX buffers and flags are in driver memory. Logical address bits and snoop mode live in `TEGRA_CEC_HW_CONTROL`. Timing and interrupt state are hardware registers. There is no persistent configuration.

## Dependencies and Integration Points
DT compatibles are `nvidia,tegra114-cec`, `nvidia,tegra124-cec`, and `nvidia,tegra210-cec`. The driver integrates with platform resources, `cec-notifier`, Tegra clocking, and optional legacy platform PM callbacks.

## Risks and Test Signals
IRQ status handling returns early for several TX errors before clearing the specific interrupt through the normal path, relying on recovery. RX overflow interrupt is defined but not enabled/handled. Suspend only disables the clock and resume only reenables it, without restoring hardware configuration. Test FIFO underrun, arbitration/bus anomaly, NACK, RX EOM collection, monitor-all toggling, logical address invalidation, and suspend/resume adapter re-enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/tegra_cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/tegra_cec.h -->
# sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/tegra_cec.h

## Purpose
This private header defines Tegra CEC register offsets, hardware-control bits, TX/RX register bit layouts, timing field shifts, interrupt status/mask bits, and debug register fields.

## Important APIs, Types, and Functions
There are no functions. Key definitions include `TEGRA_CEC_HW_CONTROL`, `TEGRA_CEC_TX_REGISTER`, `TEGRA_CEC_RX_REGISTER`, timing registers, `TEGRA_CEC_INT_STAT/MASK`, `TEGRA_CEC_HWCTRL_RX_LADDR`, `TEGRA_CEC_HWCTRL_RX_SNOOP`, TX start/EOM/retry/broadcast bits, and interrupt flags.

## Control Flow
`tegra_cec.c` uses the constants to program timing during enable, encode each transmitted byte, detect RX EOM, mask/unmask interrupts, and recover from TX failures.

## State and Persistence
The file describes hardware state only. Runtime values are in MMIO registers and driver buffers.

## Dependencies and Integration Points
It is consumed by the Tegra CEC platform driver and must match Tegra114/124/210 hardware documentation.

## Risks and Test Signals
Incorrect shift constants would corrupt timing configuration, which can look like flaky CEC signaling. Hardware register tests should validate bitfield encodings for logical-address masks, snoop mode, TX byte flags, RX EOM, and interrupt masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/tegra_cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/Kconfig

## Purpose
This Kconfig file groups USB/serial CEC adapter drivers.

## Important APIs, Types, and Functions
It does not define code APIs. Under `USB_SUPPORT && TTY`, it sources Kconfig files for Extron DA HD 4K Plus, Pulse Eight, and RainShadow drivers.

## Control Flow
Menu inclusion is conditional on USB and TTY support because these drivers bind through USB ACM/serio serial transport.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
It integrates child Kconfig menus with the media CEC build. Child drivers select `CEC_CORE`, USB, USB ACM, SERIO, and SERPORT as needed.

## Risks and Test Signals
Configuration tests should confirm child entries are hidden when TTY or USB support is unavailable and visible when prerequisites are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/Makefile

## Purpose
This Makefile builds USB/serial CEC adapter subdirectories.

## Important APIs, Types, and Functions
It maps `CONFIG_USB_EXTRON_DA_HD_4K_PLUS_CEC`, `CONFIG_USB_PULSE8_CEC`, and `CONFIG_USB_RAINSHADOW_CEC` to their respective subdirectories.

## Control Flow
Kbuild descends into selected driver directories and builds their local composite objects.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
It connects top-level CEC USB build selection to the Extron, Pulse8, and RainShadow driver implementations.

## Risks and Test Signals
Build tests should confirm each subdirectory is included only under its matching config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/Kconfig

## Purpose
This Kconfig entry enables the Extron DA HD 4K Plus HDMI splitter CEC driver.

## Important APIs, Types, and Functions
It defines `USB_EXTRON_DA_HD_4K_PLUS_CEC` as a tristate. It depends on `VIDEO_DEV`, `USB`, and `USB_ACM`, and selects `CEC_CORE`, `SERIO`, and `SERIO_SERPORT`.

## Control Flow
When enabled, the module name is `extron-da-hd-4k-plus-cec`.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The dependencies reflect that the implementation exposes V4L2 video devices and CEC adapters over a USB ACM serial line represented as a serio port.

## Risks and Test Signals
Configuration tests should verify V4L2 and USB ACM prerequisites. Since the driver uses V4L2 EDID ioctls, missing `VIDEO_DEV` would break the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/Makefile

## Purpose
This Makefile builds the Extron DA HD 4K Plus CEC module.

## Important APIs, Types, and Functions
It composes `extron-da-hd-4k-plus-cec.o` from `extron-da-hd-4k-plus.o` and `cec-splitter.o`, and maps it to `CONFIG_USB_EXTRON_DA_HD_4K_PLUS_CEC`.

## Control Flow
Kbuild links the device/protocol driver and shared splitter policy helper into one module.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
This build composition allows `extron-da-hd-4k-plus.c` to call the local splitter policy functions without exporting them globally.

## Risks and Test Signals
Build tests should confirm both objects are included; omitting `cec-splitter.o` would leave unresolved splitter helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/cec-splitter.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/cec-splitter.c

## Purpose
This file implements high-level CEC policy for an HDMI splitter with one input and multiple outputs. It makes the splitter look coherent to upstream and downstream CEC devices by forwarding selected messages, tracking power/latency, and synthesizing replies.

## Important APIs, Types, and Functions
Exported local functions are `cec_splitter_unconfigured_output`, `cec_splitter_configured_output`, `cec_splitter_received_input`, `cec_splitter_received_output`, `cec_splitter_nb_transmit_canceled_output`, and `cec_splitter_poll`. Internal helpers send Active Source, Standby, wakeup, power-status requests, current-latency requests, averaged latency replies, and Feature Abort replies.

## Control Flow
Input-side received messages are filtered: standby/wakeup/active-source are propagated to outputs, power-status and latency requests fan out to outputs, and unsupported relevant messages return `-ENOMSG` for normal CEC handling. Output-side received messages update per-port power or latency state, answer sink requests, and handle active-source/set-stream-path logic. Non-blocking transmit callbacks and periodic polling clear timed-out pending requests and synthesize fallback state.

## State and Persistence
State is in `struct cec_splitter` and `struct cec_splitter_port`: standby flag, per-output active-source, sink presence, pending sequence IDs, timestamps, video latency, and power status. No persistent storage exists.

## Dependencies and Integration Points
The file depends on CEC core helpers such as `cec_msg_*`, `cec_ops_*`, `cec_transmit_msg`, adapter configuration state, and adapter locks for timeout updates. It is used by the Extron driver when `vendor_id` enables driver-managed splitter behavior.

## Risks and Test Signals
Risks include stale sequence tracking, timeout behavior tied to adapter `xfer_timeout_ms`, and lock ordering around adapter locks from poll context. Test standby/wakeup propagation, unavailable sink handling after HPD-low timeout, aggregated power-status and latency replies, Feature Abort for unavailable fanout, and canceled non-blocking transmit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/cec-splitter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/cec-splitter.h -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/cec-splitter.h

## Purpose
This header defines the state and local API for Extron splitter CEC policy.

## Important APIs, Types, and Functions
`struct cec_splitter_port` stores adapter pointer, port number, active-source flag, sink detection, pending power/latency query sequence IDs and timestamps, video latency, and power status. `struct cec_splitter` stores device, output count, output port array, request destinations, and standby state. The declared functions handle output configuration, input/output received messages, canceled output transmits, and periodic polling.

## Control Flow
The Extron adapter callbacks call these functions when ports are configured/unconfigured, when CEC messages are received, when non-blocking transmits fail, and once per second from the setup thread.

## State and Persistence
All fields are volatile runtime policy state. `STATE_CHANGE_MAX_REPEATS` defines a repeat limit for state-change behavior, though this header’s constant is not used in the reviewed implementation.

## Dependencies and Integration Points
The header forward-declares the splitter and relies on CEC adapter types from including source files. It is private to the Extron module.

## Risks and Test Signals
State fields are updated from workqueue and polling contexts, so tests should verify synchronized access through the owning driver and adapter locks. Sequence IDs use the high bit as an internal marker, which should be preserved consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/cec-splitter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/extron-da-hd-4k-plus.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/extron-da-hd-4k-plus.c

## Purpose
This is a serio-based driver for Extron DA HD 4K Plus HDMI splitters. It manages the device over the Extron serial protocol, exposes one CEC adapter per HDMI input/output port, exposes V4L2 EDID controls per port, and optionally manages splitter CEC policy internally.

## Important APIs, Types, and Functions
Core protocol helpers are `extron_send_byte`, `extron_send_len`, `extron_send_and_wait_len`, and `extron_interrupt`. EDID helpers include `extron_parse_edid`, `extron_update_edid`, `extron_write_edid`, `extron_read_edid`, and `update_edid_work`. CEC callbacks are `extron_cec_adap_enable`, `extron_cec_adap_log_addr`, `extron_cec_adap_transmit`, configuration callbacks, canceled-transmit callback, status callback, and received-message callback. V4L2 ioctl handlers implement querycap, input/output enumeration, EDID get/set, and log status.

## Control Flow
Serio connect allocates global state, registers a V4L2 device, opens serio, and starts a setup kthread. The setup thread waits for command responsiveness, queries model/name/firmware/type/CEC engine, configures HPD behavior, allocates ports/adapters/video devices, enables CEC manual mode, initializes logical addresses, queries signal/EDID states, registers video devices and CEC adapters, optionally sets driver-managed log addresses, and then polls once per second. The interrupt parser accumulates CR/LF-delimited replies, dispatches signal/HDCP/CEC/physical-address/EDID events, and completes synchronous command waits.

## State and Persistence
`struct extron` holds serial connection, port arrays, unit metadata, V4L2 device, EDID serialization state, command reply buffers, and setup thread. `struct extron_port` holds per-port CEC/V4L2 state, EDID buffers, control state, queued RX messages, TX completion status, physical address, hotplug/signal flags, and splitter-port policy. Persistent device state can be changed through Extron commands for CEC enable/manual mode, logical addresses, HPD behavior, and written EDID.

## Dependencies and Integration Points
The driver binds to `SERIO_EXTRON_DA_HD_4K_PLUS`, uses CEC core, V4L2 controls and EDID ioctls, serio, kthreads, workqueues, completions, and local splitter policy. Module parameters tune debug, CEC vendor ID, EDID manufacturer name, and HPD behavior.

## Risks and Test Signals
This driver has many asynchronous paths: command completion, serio interrupt parsing, per-port workqueues, setup thread, delayed EDID work, and disconnect cleanup. EDID writes always upload 256 bytes even for one-block sources. Tests should cover unsupported model/firmware rejection, power-up delay path, disconnect during setup or EDID read, malformed serial replies, RX queue overflow, V4L2 EDID get/set, HPD state changes, physical address updates, manual vs vendor-managed CEC modes, and splitter polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/extron-da-hd-4k-plus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/extron-da-hd-4k-plus.h -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/extron-da-hd-4k-plus.h

## Purpose
This header defines global and per-port state for the Extron DA HD 4K Plus driver.

## Important APIs, Types, and Functions
`struct extron_port` embeds `struct cec_splitter_port`, a CEC adapter, V4L2 video device/control handler, EDID buffers and capability flags, command completion fields, queued CEC RX messages, TX status, physical address update fields, signal/EDID hotplug flags, and a video-device mutex. `struct extron` embeds the splitter, serio connection, port arrays, unit metadata, V4L2 device, setup thread, delayed EDID work, EDID serialization state, command completions, and serial buffers.

## Control Flow
The implementation allocates `struct extron` at serio connect and allocates one `struct extron_port` per HDMI port during setup. The fields coordinate serial command waits, interrupt-to-workqueue delivery, EDID reads/writes, V4L2 controls, and CEC adapter callbacks.

## State and Persistence
All structure fields are runtime state except EDID data and device configuration that may be mirrored from or written to hardware. Spinlocks protect RX queue counters; mutexes serialize video-device and serial/EDID operations.

## Dependencies and Integration Points
The header includes CEC, V4L2, serio, kthread, workqueue, and local `cec-splitter.h` APIs. It is private to the Extron module.

## Risks and Test Signals
Because many flags are shared between interrupt and workqueue contexts, locking coverage around `msg_lock`, `video_lock`, `serio_lock`, and `edid_lock` is central. Tests should exercise disconnect cleanup of registered vs unregistered adapters and queued work cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/extron-da-hd-4k-plus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/Kconfig

## Purpose
This Kconfig entry enables the Pulse Eight HDMI CEC USB/serial adapter driver.

## Important APIs, Types, and Functions
It defines `USB_PULSE8_CEC` as a tristate and selects `CEC_CORE`, `USB`, `USB_ACM`, `SERIO`, and `SERIO_SERPORT`.

## Control Flow
When enabled, the module name is `pulse8-cec`.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The selects reflect the USB ACM to serio transport and CEC framework integration.

## Risks and Test Signals
Configuration tests should ensure the driver is available with USB serial prerequisites and not built without CEC core support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/Makefile

## Purpose
This Makefile builds the Pulse Eight CEC adapter driver.

## Important APIs, Types, and Functions
It maps `CONFIG_USB_PULSE8_CEC` to `pulse8-cec.o`.

## Control Flow
Kbuild includes the object according to Kconfig.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The implementation binds to a serio protocol and registers a CEC adapter.

## Risks and Test Signals
Build tests should verify module generation for `CONFIG_USB_PULSE8_CEC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/pulse8-cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/pulse8-cec.c

## Purpose
This driver supports Pulse Eight HDMI CEC adapters over a serio serial protocol. It translates the Pulse8 framed byte protocol to Linux CEC adapter operations and can restore/write persistent dongle configuration.

## Important APIs, Types, and Functions
`struct pulse8` stores serio, CEC adapter, firmware version, ping/EEPROM work, IRQ/RX queues, TX work/message/status, command completion buffers, parser state, lock, and autonomous/config flags. Protocol helpers are `pulse8_send`, `pulse8_send_and_wait_once`, and `pulse8_send_and_wait`. CEC callbacks are `pulse8_cec_adap_enable`, `pulse8_cec_adap_log_addr`, `pulse8_cec_adap_transmit`, and `pulse8_cec_adap_free`.

## Control Flow
Serio connect allocates the adapter, opens serio, queries firmware and persistent configuration, registers the adapter, optionally restores persistent config, and starts periodic ping/EEPROM work. TX is asynchronous: the CEC transmit callback stores the message and schedules `tx_work`, which sends idle time, ACK polarity, and each byte with EOM markers. The interrupt parser handles escaped frames between `MSGSTART` and `MSGEND`, queues received CEC frames, captures command replies, and reports TX status through workqueue context.

## State and Persistence
Runtime state includes parser state, command reply data, queued RX messages, one pending TX message, and CEC config flags. Persistent dongle state can be read from firmware and written to EEPROM via `MSGCODE_WRITE_EEPROM` when `persistent_config` is enabled and configuration changed.

## Dependencies and Integration Points
The driver binds to `SERIO_PULSE8_CEC`, uses CEC core monitor/physical-address capabilities, serio, workqueues, completions, and module parameters `debug` and `persistent_config`.

## Risks and Test Signals
Risks include command/async frame interleaving, one-second command timeouts, TX work racing with disconnect, and broadcast NACK suppression. Firmware-version branches differ for HDMI version and auto-power commands. Test frame escaping, RX queue overflow, firmware <2 behavior, autonomous restore, EEPROM write scheduling, all TX failure codes, CEC logical address programming, and serio disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/pulse8-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/Kconfig

## Purpose
This Kconfig entry enables the RainShadow Tech HDMI CEC USB/serial adapter driver.

## Important APIs, Types, and Functions
It defines `USB_RAINSHADOW_CEC` as a tristate and selects `CEC_CORE`, `USB`, `USB_ACM`, `SERIO`, and `SERIO_SERPORT`.

## Control Flow
When enabled, the module name is `rainshadow-cec`.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The selections match a USB ACM device exposed through serio and integrated with the CEC core.

## Risks and Test Signals
Configuration tests should verify availability only with USB/serio dependencies and correct module naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/Makefile

## Purpose
This Makefile builds the RainShadow CEC adapter driver.

## Important APIs, Types, and Functions
It maps `CONFIG_USB_RAINSHADOW_CEC` to `rainshadow-cec.o`.

## Control Flow
Kbuild includes the driver object when configured.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The implementation binds to a serio protocol and registers a CEC adapter.

## Risks and Test Signals
Build tests should verify object inclusion for `CONFIG_USB_RAINSHADOW_CEC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/rainshadow-cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/rainshadow-cec.c

## Purpose
This driver supports RainShadow Tech HDMI CEC adapters over an ASCII serio protocol. It registers a CEC adapter and translates text commands/replies to CEC RX/TX events.

## Important APIs, Types, and Functions
`struct rain` stores device, serio, CEC adapter, command completion, worker, low-level character ring buffer, command parser buffer, command reply, and write mutex. Main functions are `rain_interrupt`, `rain_irq_work_handler`, `rain_process_msg`, `rain_send`, `rain_send_and_wait`, `rain_setup`, and CEC callbacks `rain_cec_adap_enable`, `rain_cec_adap_log_addr`, and `rain_cec_adap_transmit`.

## Control Flow
Serio connect allocates the adapter, opens serio, queries firmware/reply configuration, registers the adapter, and updates `dev`. Incoming characters are buffered in interrupt context and parsed in workqueue context. Commands start with `?`, end with CR, and either represent received/status CEC messages or synchronous setup replies. Transmit sends `!x...~` ASCII commands and completion is later reported by `STA` parser messages.

## State and Persistence
State is volatile: ring buffer indices, command parse state, latest command reply, and adapter state. The setup sends configuration/address commands but does not implement persistent storage management.

## Dependencies and Integration Points
The driver binds to `SERIO_RAINSHADOW_CEC`, uses CEC core with physical address and monitor-all capabilities, and relies on serio plus workqueues/completions.

## Risks and Test Signals
The ring buffer uses `& 0xff`, which assumes `DATA_SIZE == 256`; changes must preserve power-of-two sizing. ASCII parsing is permissive and maps unknown TX status to low-drive. Test buffer overflow, malformed hex, firmware setup failures, polling one-byte messages, logical address invalid mapping to unregistered, TX status mapping, and disconnect while commands are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/rainshadow-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/common/Kconfig

## Purpose
This Kconfig file defines common media-driver options and includes common helper subtrees.

## Important APIs, Types, and Functions
It defines common tristate options such as `CYPRESS_FIRMWARE`, `TTPCI_EEPROM`, `UVC_COMMON`, `VIDEO_CX2341X`, and `VIDEO_TVEEPROM`, plus `MEDIA_COMMON_OPTIONS` as a menu gate. It sources Kconfig files for `b2c2`, `saa7146`, `siano`, `v4l2-tpg`, and `videobuf2`.

## Control Flow
The file contributes selectable helper libraries to the media Kconfig tree. Some options depend on `USB` or `I2C`.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
It is the aggregation point for common media support code shared by multiple drivers, including the B2C2 FlexCop support researched in this shard.

## Risks and Test Signals
Configuration tests should ensure helper dependencies are correct and subtrees are visible in the expected menu context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/common/Makefile

## Purpose
This Makefile builds common media helper directories and objects.

## Important APIs, Types, and Functions
It always descends into `b2c2/`, `saa7146/`, `siano/`, `v4l2-tpg/`, and `videobuf2/`, and conditionally builds helper objects such as `cypress_firmware.o`, `ttpci-eeprom.o`, `uvc.o`, `cx2341x.o`, and `tveeprom.o`.

## Control Flow
Kbuild uses selected config symbols to include optional common objects while always entering common subdirectories.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The B2C2 subdirectory participates through its own Makefile and Kconfig. The comment asks that object entries remain alphabetically sorted by Kconfig name.

## Risks and Test Signals
Build tests should verify optional helper objects are only included with their configs and that subdirectory recursion does not introduce unwanted objects unless their local configs are selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/Kconfig

## Purpose
This Kconfig file defines common support for B2C2 FlexCop DVB devices shared by PCI and USB front-end drivers.

## Important APIs, Types, and Functions
`DVB_B2C2_FLEXCOP` is a tristate depending on `DVB_CORE`, `I2C`, and either PCI or USB FlexCop driver selection. It defaults to `y` when a bus driver is selected and auto-selects many demodulator/tuner/LNB helper drivers under `MEDIA_SUBDRV_AUTOSELECT`. `DVB_B2C2_FLEXCOP_DEBUG` is a bool selected through bus drivers.

## Control Flow
The common FlexCop object is enabled when either bus-specific driver needs it. Auto-selection pulls in possible frontend drivers so runtime probing can try multiple board variants.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
This config drives the common object built from FlexCop core, I2C, SRAM, EEPROM, FE/tuner, misc, and hardware filter code.

## Risks and Test Signals
Configuration coverage should verify all optional frontend attach paths are reachable only when their selected modules are built-in/reachable. Missing auto-selected dependencies lead to skipped attach functions at compile time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/Makefile

## Purpose
This Makefile builds the common B2C2 FlexCop DVB support object.

## Important APIs, Types, and Functions
It composes `b2c2-flexcop.o` from `flexcop.o`, `flexcop-fe-tuner.o`, `flexcop-i2c.o`, `flexcop-sram.o`, `flexcop-eeprom.o`, `flexcop-misc.o`, and `flexcop-hw-filter.o`. It maps that composite object to `CONFIG_DVB_B2C2_FLEXCOP`.

## Control Flow
Kbuild links all common FlexCop components together, with include paths added for DVB frontend and tuner headers.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
Bus-specific PCI/USB FlexCop drivers depend on this common object for shared device initialization, frontend discovery, I2C, SRAM, EEPROM, and filtering support.

## Risks and Test Signals
Build tests should confirm include paths cover all optional frontend/tuner headers and that all referenced common helpers are linked into the composite object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-common.h

## Purpose
This is the common private header for B2C2 FlexCop PCI/USB DVB device support. It defines core shared data structures, logging macros, initialization state bits, callback contracts, and cross-file prototypes.

## Important APIs, Types, and Functions
Key types are `struct flexcop_dma`, `struct flexcop_i2c_adapter`, and `struct flexcop_device`. `flexcop_device` aggregates device identity, DVB adapter/frontend/demux/net/dmxdev state, three I2C adapters, feed/filter state, bus-specific callbacks for IBI register access, I2C requests, streaming control, and MAC retrieval. The header declares prototypes for common device lifecycle, DMA, EEPROM MAC check, I2C, SRAM, frontend init/exit, revision naming, hardware filtering, SMC, and MAC filter control.

## Control Flow
Bus-specific drivers allocate/fill `flexcop_device`, provide callbacks, then call common initialization. Common components coordinate through the structure and state bits such as `FC_STATE_DVB_INIT`, `FC_STATE_I2C_INIT`, and `FC_STATE_FE_INIT`.

## State and Persistence
The structure holds all shared runtime state for a FlexCop adapter. EEPROM MAC data can be read into `dvb_adapter.proposed_mac`, but the header itself does not persist data.

## Dependencies and Integration Points
It depends on `flexcop-reg.h`, DVB demux/net/frontend APIs, PCI DMA types, mutexes, and I2C. It is included by common and bus-specific FlexCop sources.

## Risks and Test Signals
Because callbacks are bus-specific, initialization must verify all required function pointers before use. Tests should cover lifecycle state-bit cleanup, feedcount/PID filtering transitions, I2C adapter indexing, and proposed MAC propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-eeprom.c

## Purpose
This file implements FlexCop EEPROM access currently used for MAC address reading. It reads an LRC-protected MAC record from the card EEPROM through the common I2C request callback.

## Important APIs, Types, and Functions
`calc_lrc` computes XOR LRC. `flexcop_eeprom_request` retries EEPROM reads/writes against chip address `0x50 | ((addr >> 8) & 3)` using `fc->fc_i2c_adap[1]`. `flexcop_eeprom_lrc_read` validates LRC. The exported API is `flexcop_eeprom_check_mac_addr`.

## Control Flow
The MAC check reads eight bytes from EEPROM address `0x3f8`, validates the LRC over the first seven bytes, and copies the first six bytes into `fc->dvb_adapter.proposed_mac` for normal MAC mode. Extended EUI64 mode is recognized but rejected with `-EINVAL`.

## State and Persistence
The active code only reads EEPROM. Disabled `#if 0` code documents possible write/unlock helpers but is not compiled. Successful reads update the in-memory proposed MAC.

## Dependencies and Integration Points
It depends on `flexcop.h` and the bus-specific `i2c_request` callback. The PCI part uses this common path; USB has its own MAC retrieval path according to the header comment.

## Risks and Test Signals
Retries stop on `ret == 0`; nonzero bus errors are returned after all attempts. LRC failure returns `-EINVAL`. Test valid MAC, bad LRC, I2C retry success/failure, and extended-mode rejection. Ensure I2C adapter index 1 is initialized before calling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-fe-tuner.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-fe-tuner.c

## Purpose
This file detects and attaches DVB frontends/tuners/LNB controllers for B2C2 FlexCop-based cards. It supports multiple SkyStar, AirStar, CableStar, and SkyStar S2 variants by trying a table of attach functions.

## Important APIs, Types, and Functions
The exported APIs are `flexcop_frontend_init` and `flexcop_frontend_exit`. Helper functions include firmware request bridging, voltage/tone/DiSEqC control, sleep wrapping, board-specific frontend attach routines, symbol-rate setup for STV0299, and demod init tables for MT352/STV0297. The `FE_SUPPORTED` macro compiles attach paths only when the corresponding frontend drivers are reachable.

## Control Flow
`flexcop_frontend_init` iterates `flexcop_frontends`, sets `fc->dev_type` before each try, calls the attach function against `fc_i2c_adap[0]`, detaches partial frontends on failure, and registers the first successful frontend with the DVB adapter. Attach functions may configure `no_base_addr`, attach demodulators, tuner PLLs, LNB controllers, tune I2C clocking, override frontend ops, and set workarounds such as skipped PID filters. Exit unregisters and detaches the frontend if initialized.

## State and Persistence
Runtime state changes include `fc->fe`, `fc->fe_sleep`, `fc->dev_type`, `fc->init_state`, `fc_i2c_adap[*].no_base_addr`, and `skip_6_hw_pid_filter`. No persistent storage is written. Firmware may be requested for supported demods through `request_firmware`.

## Dependencies and Integration Points
The file integrates with many DVB frontend/tuner drivers: MT312, STV0299, S5H1420, ITD1000, CX24113/23/20, ISL6421, MT352, BCM3510, NXT200X, LGDT330X, simple tuner, DVB PLL, and STV0297. It relies on FlexCop IBI register callbacks for LNB voltage/tone and I2C adapters for attachment.

## Risks and Test Signals
Board probing is order-dependent and mutates state before success; failed paths must reset `no_base_addr` and detach partial frontends. Some failure paths after attaching a demod or LNB do not fully undo all changes. Test each supported board combination with reachable modules, failure fallback between attach paths, DiSEqC timing, voltage/tone register writes, frontend registration failure cleanup, firmware request propagation, and `flexcop_frontend_exit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-fe-tuner.c -->
