# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ahb.h

Purpose: Header for ath10k AHB platform support. It defines the AHB-private state, IPQ4019 control register constants, reset/clock-related offsets, halt protocol values, and init/exit stubs.

Important APIs/types/functions: `struct ath10k_ahb` stores the platform device, main device MMIO, GCC/TCSR mappings, IRQ, clocks (`cmd`, `ref`, `rtc`), and reset controls (`core_cold`, `radio_cold`, `radio_warm`, `radio_srif`, `cpu_init`). Register constants cover GCC and TCSR base/size, PLL divider, scratch register, WLAN core ID, global clock disable bits, WCSS halt request/ack pairs, halt timeout, and core CPU interrupt mask. `ath10k_ahb_init` and `ath10k_ahb_exit` are real declarations under `CONFIG_ATH10K_AHB` and no-op stubs otherwise.

Control flow: The C file uses the constants to map shared control registers, write clock information, select per-core halt registers, request AXI halt, gate core clocks, assert/deassert reset controls, and wake target CPU. The stubs let common ath10k module code call AHB init/exit unconditionally.

State/persistence: Holds runtime platform-resource handles only. No persistent data.

Dependencies/integration: Integrates with Linux `platform_device`, clk, reset controller, AHB C implementation, and PCI-private ath10k structures that embed this AHB state.

Risks: Constants are SoC-specific; using them on non-IPQ4019-compatible hardware would access wrong registers. Stub behavior must match module init ordering so non-AHB builds remain linkable.

Test signals: Successful AHB build with and without `CONFIG_ATH10K_AHB`, correct DT probe, and observed halt/reset behavior on both WLAN core IDs validate this header.
