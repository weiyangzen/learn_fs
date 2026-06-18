# sources/distributed-fs/ceph-client/drivers/mmc/host/toshsd.h

Purpose: this header describes the Toshiba PCI SD controller register map and the driver's private host structure. It is paired with `toshsd.c` and contains PCI config-space offsets, SD/SDIO MMIO register offsets, clock/power/card option bits, command encoding values, interrupt/status/error masks, and `struct toshsd_host`.

Important APIs, types, and functions: there are no functions exported from this header. The central type is `struct toshsd_host`, which owns the PCI and MMC device pointers, spinlock, current request/command/data pointers, `sg_mapping_iter` for PIO, and mapped MMIO base. Important constants include PCI clock/power/LED registers (`SD_PCICFG_*`), SD command/data/status registers (`SD_CMD`, `SD_CARDSTATUS`, `SD_DATAPORT`, `SD_INTMASKCARD`), SDIO offsets, clock divider bits, card option flags, response command encodings, STOP/internal action flags, and detailed error masks.

Control flow: `toshsd.c` uses these definitions to initialize PCI config space and MMIO registers, compose commands in `toshsd_start_cmd()`, set bus clock/power/width in `__toshsd_set_ios()`, identify card/status/data interrupts in `toshsd_irq()`, and decode detailed error status for logging. The `IRQ_DONT_CARE_BITS` mask filters status bits that should not drive IRQ dispatch.

State and persistence: the header defines where persistent hardware state lives: PCI config bytes hold clock stop/gate/mode, power, card-detect, slot, and LED controls; MMIO registers hold active commands, arguments, responses, card status, interrupt masks, transfer length/count, options, data port, transaction control, and software reset. The host structure stores volatile software state only.

Dependencies and integration points: it depends on kernel bit macros and MMC/PCI types through the C file includes. Its constants align the Toshiba-specific hardware with the generic MMC host callbacks implemented in `toshsd.c`.

Risks: many constants encode poorly documented hardware behavior, including duplicated card-present bits, SDIO-base aliases, and detailed error fields spanning two status registers. Width/timeout/card-option values are hard-coded by the driver. Any mismatch in these definitions directly affects raw MMIO and PCI config writes.

Test signals: compile coverage of `toshsd.c`, correct interrupt masking with `IRQ_DONT_CARE_BITS`, expected command and response encodings on real hardware, card option writes for 1-bit and 4-bit bus modes, error-detail logs matching injected CRC/timeout faults, and power/clock/LED config writes during probe, IOS changes, suspend, and remove.
