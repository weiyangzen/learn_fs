# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/hif.h

Purpose: defines the ath10k Host Interface abstraction used by core, BMI, HTC, HTT, debug, and bus-specific implementations. It lets common code send frames, exchange bootloader messages, read/write diagnostics, map HTC services to pipes, power/suspend devices, and fetch target information independent of bus type.

Important APIs/types/functions: `enum ath_dbg_mode`, `struct ath10k_hif_sg_item`, and `struct ath10k_hif_ops` define the interface. Inline wrappers dispatch `tx_sg`, diagnostic access, BMI exchange, start/stop, service pipe mapping, completion polling, queue availability, register access, power, suspend/resume, calibration fetch, target-info fetch, and firmware log mode.

Control flow: boot powers up, exchanges BMI, starts HIF, maps HTC services, then HTC/HTT submit SG transfers through `ath10k_hif_tx_sg`. Recovery/debug paths use optional polling and diagnostic/register helpers.

State and persistence: the header owns no storage; it standardizes calls into `ar->hif.ops`. Optional wrappers return `-EOPNOTSUPP`, no-op, or a sentinel value. No persistent state exists.

Dependencies/integration: depends on `core.h`, `bmi.h`, and `debug.h`; used by bus drivers, firmware loading, HTC, HTT, and diagnostics. The contract requires valid mandatory callbacks, DMA addresses for non-HL sends, and pipe mappings matching firmware HTC services.

Risks: mandatory callbacks are dereferenced directly; unsupported optional `read32` returns `0xdeaddead`; optional operation availability varies by bus; `transfer_context == NULL` changes completion ownership expectations.

Test signals: compile/probe every bus, fake-HIF callback dispatch tests, firmware boot, HTC timeout polling, WMI/HTT/pktlog service mapping, unsupported suspend/resume and diagnostic paths, and SG completion behavior.
