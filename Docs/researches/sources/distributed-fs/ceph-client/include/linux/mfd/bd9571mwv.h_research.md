## sources/distributed-fs/ceph-client/include/linux/mfd/bd9571mwv.h

Purpose: This header defines register and IRQ constants for ROHM BD9571MWV-M and BD9574MWF-M PMIC MFD support, especially backup mode, DVFS/AVS, GPIO, protection, and interrupt handling.

Important APIs, types, and constants: Register constants include vendor/product/revision identification, I2C/FUSA controls, backup mode control/status/recovery/timers, AVS monitoring and VID registers, DVFS initialization/set/max/boost/monitor registers, GPIO direction/output/input/debounce/interrupt/mask, keep registers, protection and system error status registers, interrupt request/mask, BD9574-specific SSCG and reset/protection controls, and the access key. Product-code constants distinguish BD9571MWV and BD9574MWF. Interrupt request bit masks map mode, protection, GPIO, 128-hour/BKUP_HOLD, watchdog, and backup-trigger events. `enum bd9571mwv_irqs` defines the regmap IRQ indexes.

Control flow: The header is declarative. MFD probe validates vendor/product ID, configures regmap and regmap IRQs, then child drivers use register constants for regulators, GPIO, watchdog/backup, and system status.

State and persistence: Backup/keep registers and PMIC protection logs can persist through some system power states. Runtime kernel state is outside this header.

Dependencies and integration points: Includes device and regmap headers. Integrates with Renesas/R-Car board power management, regulator/DVFS control, GPIO, and interrupt consumers.

Risks: BD9574-specific registers overlap the common namespace but are not valid on BD9571. Backup/DDR keep-on bits control critical retention rails. Access-key protected writes must be sequenced correctly by implementation code.

Test signals: Verify vendor/product ID detection for both products, IRQ mapping for every `BD9571MWV_IRQ_*`, GPIO interrupt behavior, DVFS voltage programming, backup-mode retention bits, and protection/error status reporting.
